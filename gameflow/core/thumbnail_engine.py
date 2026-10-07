import logging
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from gameflow.config.settings import THUMBNAILS_DIR
from gameflow.core.video_engine import video_engine

logger = logging.getLogger(__name__)

class ThumbnailEngine:
    """Creates high-CTR gaming thumbnails and covers using PIL and AI prompts."""

    def __init__(self):
        self.output_dir = THUMBNAILS_DIR

    def enhance_frame(self, img: Image.Image) -> Image.Image:
        """Applies gaming visual pop: contrast, saturation and sharpness."""
        # Saturation boost
        converter = ImageEnhance.Color(img)
        img = converter.enhance(1.35)
        # Contrast boost
        converter = ImageEnhance.Contrast(img)
        img = converter.enhance(1.25)
        # Sharpness boost
        converter = ImageEnhance.Sharpness(img)
        img = converter.enhance(1.4)
        return img

    def get_font(self, size: int) -> ImageFont.ImageFont:
        """Attempts to load a bold font or defaults to basic font."""
        font_names = [
            "C:\\Windows\\Fonts\\impact.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
            "C:\\Windows\\Fonts\\seguisb.ttf",
            "impact.ttf", "arialbd.ttf"
        ]
        for font_path in font_names:
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue
        return ImageFont.load_default()

    def generate_thumbnail_from_video(
        self,
        video_path: str,
        timestamp_sec: float,
        title_text: str = "1000 IQ CLUTCH!",
        badge_text: str = "INSANE",
        aspect_ratio: str = "16:9",  # "16:9" or "9:16"
        output_filename: str = "thumbnail.jpg",
        border_color: str = "#FF0055"
    ) -> str:
        """Extracts a frame and generates a professional gaming thumbnail."""
        temp_frame_path = str(self.output_dir / "raw_frame.jpg")
        success = video_engine.extract_frame(video_path, timestamp_sec, temp_frame_path)
        
        target_size = (1280, 720) if aspect_ratio == "16:9" else (1080, 1920)
        
        if success and Path(temp_frame_path).exists():
            base_img = Image.open(temp_frame_path).convert("RGBA")
            base_img = base_img.resize(target_size, Image.Resampling.LANCZOS)
        else:
            # Fallback to stylish dark gaming background
            base_img = Image.new("RGBA", target_size, color=(20, 20, 28, 255))

        # Enhance colors
        base_rgb = base_img.convert("RGB")
        enhanced_rgb = self.enhance_frame(base_rgb)
        img = enhanced_rgb.convert("RGBA")

        draw = ImageDraw.Draw(img)
        w, h = target_size

        # 1. Vignette / Dark gradient at the bottom & top for text readability
        overlay = Image.new("RGBA", target_size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        # Top banner shade
        overlay_draw.rectangle([0, 0, w, int(h * 0.28)], fill=(0, 0, 0, 140))
        # Bottom banner shade
        overlay_draw.rectangle([0, int(h * 0.72), w, h], fill=(0, 0, 0, 160))
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)

        # 2. Draw Eye-Catching Badge in Top Left (e.g. "INSANE", "1v5 ACE")
        if badge_text.strip():
            badge_font = self.get_font(int(h * 0.065))
            badge_str = badge_text.strip().upper()
            bbox = draw.textbbox((0, 0), badge_str, font=badge_font)
            bw = bbox[2] - bbox[0] + 40
            bh = bbox[3] - bbox[1] + 20
            bx, by = 40, 40
            
            # Badge background (Yellow or Neon Red)
            draw.rectangle([bx, by, bx + bw, by + bh], fill=(255, 40, 40, 240))
            draw.text((bx + 20, by + 8), badge_str, fill="white", font=badge_font)

        # 3. Draw Massive Main Gaming Title Text
        if title_text.strip():
            font_size = int(h * 0.12) if aspect_ratio == "16:9" else int(h * 0.08)
            main_font = self.get_font(font_size)
            text_str = title_text.strip().upper()
            
            bbox = draw.textbbox((0, 0), text_str, font=main_font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            
            tx = (w - tw) // 2
            ty = int(h * 0.76) if aspect_ratio == "16:9" else int(h * 0.45)

            # Draw thick black stroke / outline
            stroke_width = max(4, int(font_size * 0.08))
            for offset_x in range(-stroke_width, stroke_width + 1):
                for offset_y in range(-stroke_width, stroke_width + 1):
                    if offset_x != 0 or offset_y != 0:
                        draw.text((tx + offset_x, ty + offset_y), text_str, font=main_font, fill="black")
            
            # Main text in vibrant neon yellow or white
            draw.text((tx, ty), text_str, font=main_font, fill="#FFDD00")

        # 4. Outer Accent Border
        if border_color:
            border_w = 12
            draw.rectangle([0, 0, w, h], outline=border_color, width=border_w)

        # Save result
        out_path = self.output_dir / output_filename
        final_rgb = img.convert("RGB")
        final_rgb.save(out_path, quality=95)
        return str(out_path)

    def generate_ai_thumbnail_prompt(self, video_title: str, game_name: str) -> str:
        """Generates an image generation prompt for Midjourney, DALL-E 3 or Flux."""
        return (
            f"Hyper-detailed, vibrant esports YouTube gaming thumbnail for '{game_name}'. "
            f"Featuring '{video_title}'. High-energy action scene, dramatic neon lighting (magenta and cyan), "
            f"cinematic composition, dynamic angle, 8k resolution, trending on ArtStation, Unreal Engine 5 render style."
        )

thumbnail_engine = ThumbnailEngine()
