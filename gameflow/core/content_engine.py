import json
import logging
import re
from typing import Dict, Any, List, Optional
from gameflow.config.settings import (
    GEMINI_API_KEY,
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    DEFAULT_AI_PROVIDER
)
from gameflow.core.memory import agent_memory
from gameflow.skills.viral_hooks import VIRAL_GAMING_HOOKS
from gameflow.skills.platform_templates import PLATFORM_PROMPT_TEMPLATES

logger = logging.getLogger(__name__)

class ContentEngine:
    """Generates viral titles, descriptions, hashtags and social copies per platform."""

    def __init__(self):
        self.provider = DEFAULT_AI_PROVIDER

    def _call_gemini(self, prompt: str) -> str:
        """Invokes Google Gemini model."""
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise e

    def _call_openai(self, prompt: str) -> str:
        """Invokes OpenAI model."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return res.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise e

    def _call_anthropic(self, prompt: str) -> str:
        """Invokes Claude model."""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=ANTHROPIC_API_KEY)
            res = client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return res.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise e

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Cleans markdown JSON block and parses dict."""
        try:
            clean = re.sub(r"^```json\s*", "", text.strip(), flags=re.MULTILINE)
            clean = re.sub(r"^```\s*", "", clean, flags=re.MULTILINE)
            clean = clean.strip()
            return json.loads(clean)
        except Exception:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                return json.loads(text[start:end+1])
            raise ValueError(f"Could not parse JSON from: {text[:200]}")

    def _generate_offline(self, platform: str, game_name: str, gameplay_description: str) -> Dict[str, Any]:
        """Provides high-quality heuristic generation when no API key is available."""
        game_slug = game_name.replace(" ", "")
        
        if platform == "youtube":
            return {
                "titles": [
                    f"1000 IQ {game_name.upper()} CLUTCH! (Bunu Nasıl Yaptım?!)",
                    f"{game_name} Tarihinin En İnanılmaz Anı! #Shorts",
                    f"Rakipler Hile Sandı! İmkansız {game_name} Zaferi"
                ],
                "selected_title": f"1000 IQ {game_name.upper()} CLUTCH! (Bunu Nasıl Yaptım?!)",
                "description": (
                    f"Bu videoda {game_name} oyununda nefes kesen anları derledik!\n\n"
                    f"Detay: {gameplay_description}\n\n"
                    f"Beğendiyseniz kanala abone olmayı ve videoyu beğenmeyi unutmayın!\n\n"
                    f"Sizce bu pozisyonda en iyi hamle neydi? Yorumlarda belirtin!"
                ),
                "tags": [game_name, f"{game_name} clutch", f"{game_name} highlights", "gaming", "gameplay", "gamer", "fps"],
                "hashtags": [f"#{game_slug}", "#Gaming", "#Shorts"]
            }

        elif platform == "tiktok":
            return {
                "hook_text": "BUNA KİMSE İNANAMADI! 😱",
                "caption": f"Son saniyede maçı nasıl çevirdik? Siz olsanız ne yapardınız? 👀👇",
                "hashtags": ["#fyp", f"#{game_slug.lower()}", "#gaming", "#kesfet"]
            }

        elif platform == "instagram":
            return {
                "caption": (
                    f"Son saniyeye kadar nefesler tutuldu! 💥\n"
                    f"Böyle anlar için oynamaya devam ediyoruz. En iyi vuruşunuz neydi?\n\n"
                    f"Daha fazla gameplay için takip etmeyi unutma! 🎮"
                ),
                "hashtags": ["#reels", f"#{game_slug.lower()}", "#gamingreels", "#gamer"]
            }

        elif platform == "x":
            return {
                "tweet": f"Bunu sadece en iyi {game_name} oyuncuları yapabilir. 1v5 durumda maçı çevirdiğimiz o an:",
                "hashtags": [f"#{game_slug}", "#Gaming"]
            }
        return {}

    def generate_content_for_platform(
        self,
        platform: str,
        game_name: str,
        gameplay_description: str,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generates tailored marketing content for a given platform."""
        provider = provider or self.provider
        channel_context = agent_memory.get_summary_context()
        base_template = PLATFORM_PROMPT_TEMPLATES.get(platform, "")

        prompt = f"""
{base_template}

Kanal Bilgileri:
{channel_context}

Oyun Adı: {game_name}
Gameplay Özeti / Olay: {gameplay_description}
"""

        # Try AI provider if available, otherwise use smart offline generator
        try:
            if provider == "gemini" and GEMINI_API_KEY:
                raw = self._call_gemini(prompt)
                return self._extract_json(raw)
            elif provider == "openai" and OPENAI_API_KEY:
                raw = self._call_openai(prompt)
                return self._extract_json(raw)
            elif provider == "anthropic" and ANTHROPIC_API_KEY:
                raw = self._call_anthropic(prompt)
                return self._extract_json(raw)
            else:
                return self._generate_offline(platform, game_name, gameplay_description)
        except Exception as e:
            logger.warning(f"AI call failed ({e}), using offline generator fallback.")
            return self._generate_offline(platform, game_name, gameplay_description)

    def generate_full_package(self, game_name: str, gameplay_description: str, provider: Optional[str] = None) -> Dict[str, Any]:
        """Generates full publication package across YouTube, TikTok, Instagram, and X."""
        package = {}
        for platform in ["youtube", "tiktok", "instagram", "x"]:
            package[platform] = self.generate_content_for_platform(
                platform=platform,
                game_name=game_name,
                gameplay_description=gameplay_description,
                provider=provider
            )
        return package

content_engine = ContentEngine()
