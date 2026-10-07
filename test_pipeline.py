import os
import subprocess
from pathlib import Path
from gameflow.config.settings import INPUTS_DIR, OUTPUTS_DIR
from gameflow.core.video_engine import video_engine
from gameflow.core.content_engine import content_engine
from gameflow.core.thumbnail_engine import thumbnail_engine
from gameflow.core.social_publisher import social_publisher
from gameflow.core.memory import agent_memory
from gameflow.core.highlight_detector import highlight_detector

def create_synthetic_gameplay_clip(output_path: str, duration_sec: int = 5):
    """Creates a synthetic 1920x1080 gameplay video with audio for testing."""
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"testsrc=duration={duration_sec}:size=1920x1080:rate=30",
        "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration_sec}",
        "-c:v", "libx264", "-c:a", "aac",
        output_path
    ]
    subprocess.run(cmd, capture_output=True, check=True)

def test_full_gameflow():
    print("========================================")
    print("🚀 STARTING GAMEFLOW AUTOMATION TESTS")
    print("========================================")

    # 1. Test Clip Generation
    test_video = str(INPUTS_DIR / "synthetic_gameplay.mp4")
    print("\n[1/5] Generating synthetic test video...")
    create_synthetic_gameplay_clip(test_video, duration_sec=5)
    assert Path(test_video).exists(), "Synthetic video generation failed"
    print(f"  ✅ Synthetic video created: {test_video}")

    # 2. Test Video Processing (Trim, 9:16 Shorts with Blurred BG & Overlays)
    print("\n[2/5] Testing Video Engine (9:16 Shorts with Blurred BG & Effects)...")
    v_info = video_engine.get_video_info(test_video)
    print(f"  Input Info: {v_info['width']}x{v_info['height']}, {v_info['duration']}s, {v_info['fps']} fps")
    
    out_video = video_engine.process_video(
        input_path=test_video,
        output_filename="test_shorts_output.mp4",
        start_time=0.5,
        end_time=4.5,
        target_aspect_ratio="9:16",
        layout_mode="blur_background",
        hook_text="1v5 CLUTCH! 🔥",
        watermark_text="@TestGamer"
    )
    assert Path(out_video).exists(), "Video processing failed"
    out_info = video_engine.get_video_info(out_video)
    print(f"  Output Info: {out_info['width']}x{out_info['height']}, {out_info['duration']:.1f}s")
    assert out_info['width'] == 1080 and out_info['height'] == 1920, "Aspect ratio not 1080x1920"
    print("  ✅ Video processing passed!")
    # 2.5 Test AI Highlight & Kill Detector
    print("\n[2.5/5] Testing AI Highlight & Kill Detector (Dynamic start/end clipping)...")
    detected_clips = highlight_detector.detect_highlights(
        video_path=test_video,
        sensitivity=1.5,
        pre_roll_sec=1.0,
        post_roll_sec=1.0,
        min_clip_duration=2.0
    )
    assert len(detected_clips) > 0, "No highlights detected"
    print(f"  ✅ Highlight detector found {len(detected_clips)} clip(s). Clip 1 duration: {detected_clips[0]['duration']}s")


    # 3. Test Content Engine (Marketing algorithms & platform limits)
    print("\n[3/5] Testing Content Engine for Multi-Platform...")
    pkg = content_engine.generate_full_package(
        game_name="Valorant",
        gameplay_description="1v5 clutch with Vandal on Haven A site last second defuse"
    )
    for p in ["youtube", "tiktok", "instagram", "x"]:
        assert p in pkg, f"Missing platform {p} in content package"
        print(f"  ✅ Generated {p.upper()} package successfully")

    # Verify platform specific rules
    x_tweet = pkg["x"].get("tweet", "")
    assert len(x_tweet) <= 280, "Tweet exceeds 280 characters limit"
    assert "youtube" in pkg and "selected_title" in pkg["youtube"]
    print(f"  Sample YouTube Title: {pkg['youtube']['selected_title']}")
    print(f"  Sample Tweet: {x_tweet[:60]}...")

    # 4. Test Thumbnail Engine
    print("\n[4/5] Testing Thumbnail Engine...")
    thumb_path = thumbnail_engine.generate_thumbnail_from_video(
        video_path=out_video,
        timestamp_sec=1.0,
        title_text="1000 IQ CLUTCH!",
        badge_text="INSANE",
        aspect_ratio="16:9",
        output_filename="test_thumb.jpg"
    )
    assert Path(thumb_path).exists(), "Thumbnail creation failed"
    print(f"  ✅ Thumbnail generated: {thumb_path}")

    # 5. Test Social Publisher Export Bundler
    print("\n[5/5] Testing Social Publisher Export Bundler...")
    bundle_dir = social_publisher.create_export_bundle(
        bundle_name="test_bundle_run",
        video_path=out_video,
        thumbnail_path=thumb_path,
        content_package=pkg
    )
    assert Path(bundle_dir).exists(), "Export bundle directory missing"
    assert (Path(bundle_dir) / "youtube.txt").exists(), "YouTube copy file missing"
    assert (Path(bundle_dir) / "tiktok.txt").exists(), "TikTok copy file missing"
    assert (Path(bundle_dir) / "twitter_x.txt").exists(), "Twitter copy file missing"
    assert (Path(bundle_dir) / "bundle_manifest.json").exists(), "Manifest file missing"
    print(f"  ✅ Export bundle verified: {bundle_dir}")

    # 6. Test Memory Persistence
    agent_memory.record_video({
        "video_file": "test_shorts_output.mp4",
        "bundle": "test_bundle_run",
        "youtube_title": pkg["youtube"]["selected_title"]
    })
    hist = agent_memory.load_history()
    assert len(hist) > 0, "Memory history recording failed"
    print("  ✅ Memory persistence verified!")

    print("\n========================================")
    print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
    print("========================================")

if __name__ == "__main__":
    test_full_gameflow()
