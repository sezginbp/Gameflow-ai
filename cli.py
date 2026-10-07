import argparse
import sys
import json
from pathlib import Path
from gameflow.core.video_engine import video_engine
from gameflow.core.content_engine import content_engine
from gameflow.core.thumbnail_engine import thumbnail_engine
from gameflow.core.social_publisher import social_publisher
from gameflow.core.memory import agent_memory
from gameflow.core.highlight_detector import highlight_detector

def main():
    parser = argparse.ArgumentParser(description="GameFlow AI CLI - Automated Gameplay Studio")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Command: process
    proc_parser = subparsers.add_parser("process", help="Process video with trimming, layout and filters")
    proc_parser.add_argument("--video", required=True, help="Path to input video file")
    proc_parser.add_argument("--start", type=float, default=0.0, help="Start trim in seconds")
    proc_parser.add_argument("--end", type=float, default=None, help="End trim in seconds")
    proc_parser.add_argument("--aspect", default="9:16", choices=["9:16", "16:9", "original"])
    proc_parser.add_argument("--layout", default="blur_background", choices=["blur_background", "crop", "fit"])
    proc_parser.add_argument("--hook", default="", help="Hook banner text")
    proc_parser.add_argument("--watermark", default="", help="Watermark text")
    proc_parser.add_argument("--output", default="processed_clip.mp4", help="Output filename")

    # Command: content
    cnt_parser = subparsers.add_parser("content", help="Generate viral titles, tags and copies for platforms")
    cnt_parser.add_argument("--game", required=True, help="Game title (e.g. Valorant, GTA V)")
    cnt_parser.add_argument("--desc", required=True, help="Short summary of what happens in the gameplay")
    cnt_parser.add_argument("--provider", default="gemini", choices=["gemini", "openai", "anthropic", "offline"])

    # Command: thumbnail
    thumb_parser = subparsers.add_parser("thumbnail", help="Extract frame and generate thumbnail")
    thumb_parser.add_argument("--video", required=True, help="Video file path")
    thumb_parser.add_argument("--time", type=float, default=2.0, help="Timestamp in seconds")
    thumb_parser.add_argument("--title", default="1000 IQ CLUTCH!", help="Main bold text")
    thumb_parser.add_argument("--badge", default="INSANE", help="Corner badge text")
    thumb_parser.add_argument("--aspect", default="16:9", choices=["16:9", "9:16"])
    thumb_parser.add_argument("--output", default="thumbnail.jpg", help="Output thumbnail filename")

    # Command: auto (Full pipeline)
    auto_parser = subparsers.add_parser("auto", help="Run full pipeline: video edit + AI content + thumbnail + export bundle")
    auto_parser.add_argument("--video", required=True, help="Input video")
    auto_parser.add_argument("--game", required=True, help="Game name")
    auto_parser.add_argument("--desc", required=True, help="Gameplay description")
    auto_parser.add_argument("--aspect", default="9:16", choices=["9:16", "16:9"])
    # Command: detect (Find kill/fail moments in long video)
    detect_parser = subparsers.add_parser("detect", help="Analyze long gameplay video and detect kill/fail moments")
    detect_parser.add_argument("--video", required=True, help="Path to long gameplay video")
    detect_parser.add_argument("--sensitivity", type=float, default=1.5, help="Sensitivity (1.0 - 2.5)")
    detect_parser.add_argument("--preroll", type=float, default=4.0, help="Pre-roll seconds before kill")
    detect_parser.add_argument("--postroll", type=float, default=4.0, help="Post-roll seconds after kill")
    detect_parser.add_argument("--min-duration", type=float, default=8.0, help="Min clip duration in seconds")
    detect_parser.add_argument("--max-duration", type=float, default=60.0, help="Max clip duration in seconds")

    # Command: auto-highlights (Detect + Clip + Edit + Content + Thumbnails for all moments)
    ah_parser = subparsers.add_parser("auto-highlights", help="Detect all kill moments and produce edited clips and bundles")
    ah_parser.add_argument("--video", required=True, help="Path to long gameplay video")
    ah_parser.add_argument("--game", required=True, help="Game name")
    ah_parser.add_argument("--aspect", default="9:16", choices=["9:16", "16:9"])


    args = parser.parse_args()

    if args.command == "process":
        print(f"🎬 Processing video: {args.video}...")
        out = video_engine.process_video(
            input_path=args.video,
            output_filename=args.output,
            start_time=args.start,
            end_time=args.end,
            target_aspect_ratio=args.aspect,
            layout_mode=args.layout,
            hook_text=args.hook,
            watermark_text=args.watermark
        )
        print(f"✅ Video created: {out}")

    elif args.command == "content":
        print(f"🤖 Generating viral content package for {args.game}...")
        pkg = content_engine.generate_full_package(
            game_name=args.game,
            gameplay_description=args.desc,
            provider=args.provider
        )
        print(json.dumps(pkg, ensure_ascii=False, indent=2))

    elif args.command == "thumbnail":
        print(f"🖼️ Generating thumbnail from {args.video} at {args.time}s...")
        t_out = thumbnail_engine.generate_thumbnail_from_video(
            video_path=args.video,
            timestamp_sec=args.time,
            title_text=args.title,
            badge_text=args.badge,
            aspect_ratio=args.aspect,
            output_filename=args.output
        )
        print(f"✅ Thumbnail created: {t_out}")

    elif args.command == "auto":
        print(f"🚀 Running Full Automation Pipeline for {args.video}...")
        # 1. Video
        video_out = video_engine.process_video(
            input_path=args.video,
            output_filename=f"auto_{Path(args.video).stem}.mp4",
            target_aspect_ratio=args.aspect,
            layout_mode="blur_background" if args.aspect == "9:16" else "fit",
            hook_text="BEKLE VE GÖR! 🔥",
            watermark_text=agent_memory.profile.get("watermark_text", "@Gamer")
        )
        # 2. Content
        pkg = content_engine.generate_full_package(
            game_name=args.game,
            gameplay_description=args.desc
        )
        # 3. Thumbnail
        thumb_out = thumbnail_engine.generate_thumbnail_from_video(
            video_path=video_out,
            timestamp_sec=1.5,
            title_text=pkg.get("youtube", {}).get("selected_title", "CLUTCH!"),
            badge_text="INSANE",
            aspect_ratio="16:9"
        )
        # 4. Bundle
        bundle_name = f"auto_bundle_{Path(args.video).stem}"
        bundle_dir = social_publisher.create_export_bundle(
            bundle_name=bundle_name,
            video_path=video_out,
            thumbnail_path=thumb_out,
            content_package=pkg
        )
        agent_memory.record_video({
            "video_file": Path(video_out).name,
            "bundle": bundle_name,
            "youtube_title": pkg.get("youtube", {}).get("selected_title")
        })
        print(f"\n🎉 FULL PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"📦 Export Bundle Ready at: {bundle_dir}")

    elif args.command == "detect":
        print(f"🎯 Scanning video for Kill & Action Moments: {args.video}...")
        clips = highlight_detector.detect_highlights(
            video_path=args.video,
            sensitivity=args.sensitivity,
            pre_roll_sec=args.preroll,
            post_roll_sec=args.postroll,
            min_clip_duration=args.min_duration,
            max_clip_duration=args.max_duration
        )
        print(f"✅ Found {len(clips)} action moments:")
        print(json.dumps(clips, ensure_ascii=False, indent=2))

    elif args.command == "auto-highlights":
        print(f"🎯 Auto-processing all highlight clips from {args.video}...")
        clips = highlight_detector.detect_highlights(video_path=args.video)
        print(f"Found {len(clips)} clips to process.")
        for c in clips:
            c_id = c["clip_id"]
            print(f"\n🎬 Processing Clip #{c_id}: {c['label']} ({c['duration']}s)...")
            out_name = f"highlight_{Path(args.video).stem}_clip{c_id}.mp4"
            v_out = video_engine.process_video(
                input_path=args.video,
                output_filename=out_name,
                start_time=c["start_time"],
                end_time=c["end_time"],
                target_aspect_ratio=args.aspect,
                layout_mode="blur_background" if args.aspect == "9:16" else "fit",
                hook_text=f"CLUTCH #{c_id} 🔥",
                watermark_text=agent_memory.profile.get("watermark_text", "@Gamer")
            )
            pkg = content_engine.generate_full_package(
                game_name=args.game,
                gameplay_description=f"{c['event_type']} - {c['duration']}s gameplay clip"
            )
            t_out = thumbnail_engine.generate_thumbnail_from_video(
                video_path=v_out,
                timestamp_sec=min(2.0, c["duration"] / 2),
                title_text=pkg.get("youtube", {}).get("selected_title", f"INSANE KILL #{c_id}"),
                badge_text="CLUTCH",
                aspect_ratio="16:9"
            )
            b_name = f"bundle_{Path(args.video).stem}_clip{c_id}"
            b_dir = social_publisher.create_export_bundle(
                bundle_name=b_name,
                video_path=v_out,
                thumbnail_path=t_out,
                content_package=pkg
            )
            print(f"  ✅ Clip #{c_id} Ready: {b_dir}")
        print("\n🎉 ALL HIGHLIGHT CLIPS PROCESSED & READY!")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
