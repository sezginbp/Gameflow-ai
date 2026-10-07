import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from gameflow.config.settings import MEMORY_DIR

logger = logging.getLogger(__name__)

PROFILE_FILE = MEMORY_DIR / "channel_profile.json"
HISTORY_FILE = MEMORY_DIR / "video_history.json"

DEFAULT_PROFILE = {
    "channel_name": "GamerStudio",
    "creator_name": "PlayerOne",
    "game_niche": "Valorant & FPS Games",
    "target_language": "tr",  # tr or en
    "tone": "Energetic, Hype, High-Skill & Entertaining",
    "default_hashtags": ["#gaming", "#gamer", "#gameplay", "#shorts", "#clutch"],
    "watermark_text": "@GamerStudio",
    "preferred_aspect_ratio": "9:16",
    "bgm_volume": 0.25,
    "gameplay_volume": 1.0,
    "auto_publish": False,
    "created_at": datetime.now().isoformat()
}

class AgentMemory:
    """Persistent Agent Memory & Channel Context manager inspired by claude-mem."""

    def __init__(self):
        self.profile = self.load_profile()
        self.history = self.load_history()

    def load_profile(self) -> Dict[str, Any]:
        """Loads creator channel profile from disk."""
        if not PROFILE_FILE.exists():
            self.save_profile(DEFAULT_PROFILE)
            return DEFAULT_PROFILE.copy()
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # merge with defaults to ensure all keys exist
                merged = DEFAULT_PROFILE.copy()
                merged.update(data)
                return merged
        except Exception as e:
            logger.error(f"Error loading profile: {e}")
            return DEFAULT_PROFILE.copy()

    def save_profile(self, profile_data: Dict[str, Any]):
        """Saves creator channel profile to disk."""
        self.profile = profile_data
        try:
            with open(PROFILE_FILE, "w", encoding="utf-8") as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving profile: {e}")

    def update_field(self, key: str, value: Any):
        """Updates a single field in the profile."""
        self.profile[key] = value
        self.save_profile(self.profile)

    def load_history(self) -> List[Dict[str, Any]]:
        """Loads video processing history."""
        if not HISTORY_FILE.exists():
            return []
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            return []

    def record_video(self, record: Dict[str, Any]):
        """Records processed video details to history."""
        record["timestamp"] = datetime.now().isoformat()
        self.history.insert(0, record)
        # Keep last 100 entries
        self.history = self.history[:100]
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving history: {e}")

    def get_summary_context(self) -> str:
        """Returns channel context string for LLM prompting."""
        return (
            f"Channel Name: {self.profile.get('channel_name')}\n"
            f"Creator: {self.profile.get('creator_name')}\n"
            f"Game Niche: {self.profile.get('game_niche')}\n"
            f"Content Tone: {self.profile.get('tone')}\n"
            f"Language: {self.profile.get('target_language', 'tr').upper()}\n"
            f"Signature Tag: {self.profile.get('watermark_text')}"
        )

# Global singleton
agent_memory = AgentMemory()
