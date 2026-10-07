"""
Curated Viral Hook Formulas tailored for Gaming Content,
derived from coreyhaines31/marketingskills research and best practices.
"""

VIRAL_GAMING_HOOKS = {
    "curiosity": [
        "Kimsenin bilmediği o gizli taktik...",
        "Bunu gördüğümde gözlerime inanamadım!",
        "Bu taktiğin hala çalıştığına inanamıyorum...",
        "Oyunun en gizli mekaniğini buldum!",
        "Neden kimse bu yöntemden bahsetmiyor?",
        "Bu hatayı siz de yapıyorsanız acilen bırakın!"
    ],
    "skill_and_value": [
        "Bu taktikle derecenizi 2 kat hızla yükseltin",
        "Pro oyuncuların asla söylemediği 3 kritik ayar",
        "60 saniyede bu karakteri ustalaşma rehberi",
        "Her raundu kazandıran o tek strateji",
        "Bu tek spray kontrol tekniği hayatınızı kurtaracak"
    ],
    "shock_and_hype": [
        "1v5 İMKANSIZ CLUTCH! (Nefesler tutuldu)",
        "Tarihin en şanslı veya en zeki vuruşu?",
        "1000 IQ Hamle: Düşman takımı ne olduğunu anlamadı!",
        "Lobi şokta! Böyle bir clutch görülmedi...",
        "Hile mi yoksa saf yetenek mi? Siz karar verin!"
    ],
    "story_and_journey": [
        "Son saniyede maçı nasıl çevirdik...",
        "0-12'den maçı çevirme hikayesi!",
        "Takım arkadaşlarım oyundan çıktı, ama ben pes etmedim...",
        "Tam kaybettiğimizi sanıyorduk ki bu oldu..."
    ]
}

def get_hook_templates(category: str = "shock_and_hype") -> list:
    return VIRAL_GAMING_HOOKS.get(category, VIRAL_GAMING_HOOKS["shock_and_hype"])
