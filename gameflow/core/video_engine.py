import os
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from gameflow.config.settings import OUTPUTS_DIR

logger = logging.getLogger(__name__)

class VideoEngine:
    """High-performance FFmpeg Video Processing Engine for Gameplay Highlights."""

    def __init__(self, ffmpeg_bin: str = "ffmpeg", ffprobe_bin: str = "ffprobe"):
        self.ffmpeg = ffmpeg_bin
        self.ffprobe = ffprobe_bin

    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Extracts video metadata (duration, width, height, fps, has_audio) using ffprobe."""
        cmd = [
            self.ffprobe,
            "-v", "error",
            "-show_entries", "stream=width,height,r_frame_rate,codec_type:format=duration",
            "-of", "json",
            video_path
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(res.stdout)
            
            duration = float(data.get("format", {}).get("duration", 0.0))
            streams = data.get("streams", [])
            video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
            has_audio = any(s.get("codec_type") == "audio" for s in streams)
            
            width = int(video_stream.get("width", 1920))
            height = int(video_stream.get("height", 1080))
            
            fps_str = video_stream.get("r_frame_rate", "30/1")
            fps = 30.0
            if "/" in fps_str:
                num, den = fps_str.split("/")
                fps = float(num) / float(den) if float(den) != 0 else 30.0
            else:
                fps = float(fps_str)

            return {
                "duration": duration,
                "width": width,
                "height": height,
                "fps": round(fps, 2),
                "has_audio": has_audio,
                "aspect_ratio": "16:9" if width > height else "9:16"
            }
        except Exception as e:
            logger.error(f"Failed to probe video: {e}")
            return {
                "duration": 60.0,
                "width": 1920,
                "height": 1080,
                "fps": 30.0,
                "has_audio": True,
                "aspect_ratio": "16:9"
            }

    def extract_frame(self, video_path: str, timestamp_sec: float, output_path: str) -> bool:
        """Extracts a single high-quality frame from video at timestamp."""
        cmd = [
            self.ffmpeg,
            "-y",
            "-ss", str(timestamp_sec),
            "-i", video_path,
            "-vframes", "1",
            "-q:v", "2",
            output_path
        ]
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            return Path(output_path).exists()
        except Exception as e:
            logger.error(f"Error extracting frame: {e}")
    def process_video(
        self,
        input_path: str,
        output_filename: str,
        start_time: float = 0.0,
        end_time: Optional[float] = None,
        target_aspect_ratio: str = "9:16",  # "9:16", "16:9", "original"
        layout_mode: str = "blur_background",  # "blur_background", "crop", "fit"
        contrast: float = 1.15,
        brightness: float = 0.02,
        saturation: float = 1.25,
        enable_vignette: bool = True,
        speed_factor: float = 1.0,
        hook_text: str = "",
        watermark_text: str = "",
        bgm_path: Optional[str] = None,
        bgm_volume: float = 0.25,
        gameplay_volume: float = 1.0
    ) -> str:
        """Executes full video transformation pipeline via FFmpeg."""
        out_path = OUTPUTS_DIR / output_filename
        out_path_str = str(out_path)

        duration_args = []
        if start_time > 0:
            duration_args.extend(["-ss", str(start_time)])
        if end_time is not None and end_time > start_time:
            duration_args.extend(["-t", str(round(end_time - start_time, 3))])

        color_filter = f"eq=contrast={contrast}:brightness={brightness}:saturation={saturation}"
        if enable_vignette:
            color_filter += ",vignette=PI/4"

        filter_chains = []
        if target_aspect_ratio == "9:16":
            target_w, target_h = 1080, 1920
            if layout_mode == "blur_background":
                aspect_filter = (
                    f"split [bg][fg];"
                    f"[bg]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,"
                    f"crop={target_w}:{target_h},gblur=sigma=24,{color_filter}[bg_blur];"
                    f"[fg]scale={target_w}:-1,{color_filter}[fg_sharp];"
                    f"[bg_blur][fg_sharp]overlay=(W-w)/2:(H-h)/2"
                )
                filter_chains.append(aspect_filter)
            elif layout_mode == "crop":
                aspect_filter = f"scale=-1:{target_h},crop={target_w}:{target_h},{color_filter}"
                filter_chains.append(aspect_filter)
            else:
                aspect_filter = f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2,{color_filter}"
                filter_chains.append(aspect_filter)
        elif target_aspect_ratio == "16:9":
            target_w, target_h = 1920, 1080
            aspect_filter = f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2,{color_filter}"
            filter_chains.append(aspect_filter)
        else:
            filter_chains.append(color_filter)

        if speed_factor != 1.0 and speed_factor > 0:
            setpts = 1.0 / speed_factor
            filter_chains.append(f"setpts={setpts}*PTS")

        def clean_txt(t: str) -> str:
            return t.replace(":", "\\:").replace("'", "\\'").replace("%", "\\%")

        if hook_text.strip():
            safe_hook = clean_txt(hook_text.strip())
            drawtext_hook = (
                f"drawtext=text='{safe_hook}':"
                f"fontcolor=white:fontsize=52:box=1:boxcolor=black@0.7:boxborderw=18:"
                f"x=(w-text_w)/2:y=120"
            )
            filter_chains.append(drawtext_hook)

        if watermark_text.strip():
            safe_watermark = clean_txt(watermark_text.strip())
            drawtext_wm = (
                f"drawtext=text='{safe_watermark}':"
                f"fontcolor=yellow@0.9:fontsize=36:shadowcolor=black@0.8:shadowx=2:shadowy=2:"
                f"x=(w-text_w)/2:y=h-140"
            )
            filter_chains.append(drawtext_wm)

        final_vf = ",".join(filter_chains)

        input_files = []
        if duration_args:
            input_files.extend(duration_args)
        input_files.extend(["-i", input_path])

        filter_complex = None
        audio_maps = []

        if bgm_path and Path(bgm_path).exists():
            input_files.extend(["-stream_loop", "-1", "-i", bgm_path])
            filter_complex = (
                f"[0:v]{final_vf}[outv];"
                f"[0:a]volume={gameplay_volume}[a1];"
                f"[1:a]volume={bgm_volume}[a2];"
                f"[a1][a2]amix=inputs=2:duration=first:dropout_transition=2[outa]"
            )
            audio_maps = ["-map", "[outv]", "-map", "[outa]"]
        else:
            audio_maps = ["-vf", final_vf]
            if gameplay_volume != 1.0:
                audio_maps.extend(["-af", f"volume={gameplay_volume}"])

        cmd = [self.ffmpeg, "-y"]
        cmd.extend(input_files)

        if filter_complex:
            cmd.extend(["-filter_complex", filter_complex])
            cmd.extend(audio_maps)
        else:
            cmd.extend(audio_maps)

        cmd.extend([
            "-c:v", "libx264",
            "-preset", "faster",
            "-crf", "20",
            "-c:a", "aac",
            "-b:a", "192k",
            out_path_str
        ])

        logger.info(f"Running FFmpeg: {' '.join(cmd)}")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            logger.error(f"FFmpeg error: {res.stderr}")
            raise RuntimeError(f"Video processing failed: {res.stderr[:500]}")

        return out_path_str

video_engine = VideoEngine()
