import os
import streamlit as st
from pathlib import Path
from gameflow.config.settings import (
    INPUTS_DIR, OUTPUTS_DIR, AUDIO_DIR, THUMBNAILS_DIR,
    GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY,
    X_API_KEY, TIKTOK_ACCESS_TOKEN, INSTAGRAM_ACCESS_TOKEN
)
from gameflow.core.memory import agent_memory
from gameflow.core.video_engine import video_engine
from gameflow.core.content_engine import content_engine
from gameflow.core.thumbnail_engine import thumbnail_engine
from gameflow.core.social_publisher import social_publisher
from gameflow.core.highlight_detector import highlight_detector
from gameflow.skills.viral_hooks import VIRAL_GAMING_HOOKS

st.set_page_config(
    page_title="GameFlow AI - Gameplay Studio & Publisher",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Gamer Theme CSS
st.markdown("""
<style>
    .main { background-color: #0f1117; color: #ffffff; }
    .stButton>button {
        background: linear-gradient(90deg, #ff0055 0%, #ff5500 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(255, 0, 85, 0.4);
    }
    .card-box {
        background: #1a1d26;
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid #2a2e3d;
        margin-bottom: 1rem;
    }
    .badge {
        background-color: #ff0055;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.title("🎮 GameFlow AI")
    st.caption("AI Gameplay Video Studio & Multi-Platform Publisher")
    st.divider()

    st.subheader("👤 Kanal Profili (Ajan Hafızası)")
    profile = agent_memory.profile
    channel_name = st.text_input("Kanal Adı", value=profile.get("channel_name", "GamerStudio"))
    game_niche = st.text_input("Oyun Türü / Niche", value=profile.get("game_niche", "Valorant & FPS"))
    tone = st.text_input("İçerik Tonu", value=profile.get("tone", "Hype, Energetic, Pro"))
    watermark = st.text_input("Filigran / Tag", value=profile.get("watermark_text", "@GamerStudio"))

    if st.button("💾 Profili Kaydet", use_container_width=True):
        agent_memory.save_profile({
            **profile,
            "channel_name": channel_name,
            "game_niche": game_niche,
            "tone": tone,
            "watermark_text": watermark
        })
        st.success("Kanal hafızası güncellendi!")

    st.divider()
    st.subheader("⚡ Sistem Durumu")
    st.write("• **FFmpeg:** ✅ Aktif")
    st.write(f"• **Gemini AI:** {'✅ Hazır' if GEMINI_API_KEY else '⚠️ Anahtar Yok (Heuristic Mod)'}")
    st.write(f"• **OpenAI:** {'✅ Hazır' if OPENAI_API_KEY else '⚠️ Yok'}")
    st.write(f"• **X (Twitter):** {'✅ Bağlı' if X_API_KEY else '⚠️ Anahtar Bekleniyor'}")
    st.write(f"• **TikTok:** {'✅ Bağlı' if TIKTOK_ACCESS_TOKEN else '⚠️ Anahtar Bekleniyor'}")
    st.write(f"• **Instagram:** {'✅ Bağlı' if INSTAGRAM_ACCESS_TOKEN else '⚠️ Anahtar Bekleniyor'}")

# ----------------- MAIN TABS -----------------
tab_ai_clips, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 AI Kill & Highlight Avcısı (Akıllı Klip Kesici)",
    "🎬 Manuel Video Studio (Kırpma & Efektler)",
    "🤖 AI İçerik & Kancalar",
    "🖼️ Thumbnail Stüdyosu",
    "🚀 Çoklu Platform Paylaşım",
    "🧠 Ajan Hafızası & Geçmiş"
])

# ----------------- TAB: AI KILL & HIGHLIGHT AVCISI -----------------
with tab_ai_clips:
    st.header("🎯 AI Kill & Aksiyon Avcısı (Otomatik Klip Kesici)")
    st.write("10 dakika veya daha uzun gameplay videolarınızdaki **kill, clutch, headshot veya fail anlarını** otomatik tespit eder. Klip ne kadar sürdüyse (15s, 28s, 42s) doğal süresinde keser ve 9:16 Shorts/TikTok formatına dönüştürür.")

    col_src, col_cfg = st.columns([1, 1])

    with col_src:
        st.subheader("📹 Kaynak Video")
        raw_upload = st.file_uploader("Uzun Gameplay Videosu Yükle (MP4 / MKV)", type=["mp4", "mov", "mkv", "avi"], key="hl_uploader")
        hl_video_path = None

        if raw_upload:
            hl_video_path = str(INPUTS_DIR / raw_upload.name)
            with open(hl_video_path, "wb") as f:
                f.write(raw_upload.read())
            st.success(f"Video yüklendi: {raw_upload.name}")
        else:
            existing_vids = list(INPUTS_DIR.glob("*.mp4"))
            if existing_vids:
                sel_vid = st.selectbox("Veya Klasördeki Mevcut Videoyu Seç:", [v.name for v in existing_vids], key="hl_sel_vid")
                hl_video_path = str(INPUTS_DIR / sel_vid)

        if hl_video_path and Path(hl_video_path).exists():
            v_stat = video_engine.get_video_info(hl_video_path)
            st.video(hl_video_path)
            st.info(f"⏱️ Toplam Süre: {v_stat['duration']:.1f} saniye ({v_stat['duration']/60:.1f} dk) | 📐 {v_stat['width']}x{v_stat['height']} | 🎯 {v_stat['fps']} FPS")

    with col_cfg:
        st.subheader("⚙️ Kill & Aksiyon Yakalama Ayarları")
        hl_sensitivity = st.slider("🎯 Algılama Hassasiyeti", 1.0, 2.5, 1.5, 0.1, help="Yüksek değer daha fazla klip çıkarır, düşük değer sadece en büyük çığlık/patlama/ace anlarını yakalar.")
        
        c_pre, c_post = st.columns(2)
        with c_pre:
            pre_roll = st.slider("⏪ Kill Öncesi Süre (sn)", 1.0, 10.0, 4.0, 0.5, help="Vuruş öncesi nişan alma ve pozisyon hazırlığı.")
        with c_post:
            post_roll = st.slider("⏩ Kill Sonrası Süre (sn)", 1.0, 10.0, 4.0, 0.5, help="Vuruş sonrası killfeed, kutlama veya tepki.")

        c_min, c_max = st.columns(2)
        with c_min:
            min_dur = st.slider("⏱️ Min Klip Süresi (sn)", 5.0, 20.0, 8.0, 1.0)
        with c_max:
            max_dur = st.slider("⏳ Max Klip Süresi (sn)", 15.0, 90.0, 60.0, 5.0)

        merge_gap = st.slider("🔗 Combo / Multi-Kill Birleştirme (sn)", 2.0, 10.0, 5.0, 0.5)

        st.divider()
        st.subheader("🎨 Otomatik Edit Şablonu")
        hl_aspect = st.selectbox("Klip Formatı", ["9:16 Dikey (Shorts / Reels / TikTok)", "16:9 Yatay (YouTube)"], key="hl_aspect")
        hl_layout = st.selectbox("Shorts Yerleşimi", ["blur_background", "crop", "fit"], format_func=lambda x: "Bulanık Arka Plan + Ortalanmış Net Oyun (Pro)" if x == "blur_background" else ("Merkez Kırpma" if x == "crop" else "Siyah Çerçeveli Sığdırma"), key="hl_layout")
        hl_color_boost = st.checkbox("Canlı Gamer Renkleri (Kontrast & Doygunluk)", value=True, key="hl_color")
        hl_vignette = st.checkbox("Odak Vinyeti (Kenar Karartma)", value=True, key="hl_vig")

    st.divider()
    if hl_video_path and Path(hl_video_path).exists():
        if st.button("🚀 Videoyu Tara ve Kill/Aksiyon Anlarını Yakala", use_container_width=True):
            with st.spinner("Ses patlamaları, silah sesleri ve aksiyon anları taranıyor..."):
                detected = highlight_detector.detect_highlights(
                    video_path=hl_video_path,
                    sensitivity=hl_sensitivity,
                    pre_roll_sec=pre_roll,
                    post_roll_sec=post_roll,
                    min_clip_duration=min_dur,
                    max_clip_duration=max_dur,
                    merge_gap_sec=merge_gap
                )
                st.session_state["detected_clips"] = detected
                st.session_state["hl_source_path"] = hl_video_path
                st.success(f"🎉 Toplam {len(detected)} adet aksiyon ve kill anı başarıyla yakalandı!")

    if "detected_clips" in st.session_state and st.session_state["detected_clips"]:
        clips = st.session_state["detected_clips"]
        src_vid = st.session_state.get("hl_source_path", hl_video_path)
        st.subheader(f"📋 Yakalanan Klipler ({len(clips)} Adet)")

        for c in clips:
            c_id = c["clip_id"]
            with st.container():
                st.markdown(f"""
                <div class="card-box">
                    <span class="badge">Sıra #{c.get('rank', c_id)}</span> <b>{c['label']}</b>
                    <p style="color: #a0a5b5; margin-top: 5px;">
                        ⏱️ Zaman Aralığı: <b>{c['start_time']}s ➔ {c['end_time']}s</b> | Süre: <b>{c['duration']} saniye</b> | Hype Skoru: <b>{c['score']}</b>
                    </p>
                </div>
                """, unsafe_allow_html=True)

                col_hook, col_action = st.columns([2, 1])
                with col_hook:
                    hook_val = st.text_input(f"Klip #{c_id} Üst Kanca Yazısı", value=f"{c['event_type']} 🔥", key=f"hook_{c_id}")
                with col_action:
                    st.write("")
                    if st.button(f"🎬 Klibi 9:16 Shorts Olarak Kes", key=f"btn_cut_{c_id}", use_container_width=True):
                        with st.spinner(f"Klip #{c_id} işleniyor..."):
                            out_clip_name = f"highlight_{Path(src_vid).stem}_clip{c_id}.mp4"
                            target_ar = "9:16" if "9:16" in hl_aspect else "16:9"
                            clip_out = video_engine.process_video(
                                input_path=src_vid,
                                output_filename=out_clip_name,
                                start_time=c["start_time"],
                                end_time=c["end_time"],
                                target_aspect_ratio=target_ar,
                                layout_mode=hl_layout,
                                contrast=1.15 if hl_color_boost else 1.0,
                                saturation=1.25 if hl_color_boost else 1.0,
                                enable_vignette=hl_vignette,
                                hook_text=hook_val,
                                watermark_text=watermark
                            )
                            st.session_state[f"processed_clip_{c_id}"] = clip_out
                            st.success(f"✅ Klip #{c_id} hazırlandı!")

                if f"processed_clip_{c_id}" in st.session_state:
                    p_path = st.session_state[f"processed_clip_{c_id}"]
                    st.video(p_path)
                    with open(p_path, "rb") as vf:
                        st.download_button(f"📥 Klip #{c_id} İndir (MP4)", vf, file_name=Path(p_path).name, mime="video/mp4", key=f"dl_{c_id}")


# ----------------- TAB 1: VIDEO STUDIO -----------------
with tab1:
    st.header("🎬 Gameplay Video Düzenleme & Efektler")
    st.write("Videonuzu yükleyin, dilediğiniz filtreleri, kırpmayı, ses miksini ve kanca yazılarını ekleyin.")

    col_in, col_settings = st.columns([1, 1])

    with col_in:
        uploaded_video = st.file_uploader("Gameplay Videosu Seç / Yükle", type=["mp4", "mov", "mkv", "avi"])
        video_input_path = None

        if uploaded_video:
            video_input_path = str(INPUTS_DIR / uploaded_video.name)
            with open(video_input_path, "wb") as f:
                f.write(uploaded_video.read())
            st.success(f"Video yüklendi: {uploaded_video.name}")
            st.video(video_input_path)
            v_info = video_engine.get_video_info(video_input_path)
            st.info(f"⏱️ Süre: {v_info['duration']:.1f}s | 📐 Çözünürlük: {v_info['width']}x{v_info['height']} | 🎯 FPS: {v_info['fps']}")
        else:
            # Check for existing sample videos in inputs folder
            existing = list(INPUTS_DIR.glob("*.mp4"))
            if existing:
                selected_existing = st.selectbox("Veya mevcut dosyalardan seç:", [str(p) for p in existing])
                video_input_path = selected_existing
                st.video(video_input_path)
                v_info = video_engine.get_video_info(video_input_path)
                st.info(f"⏱️ Süre: {v_info['duration']:.1f}s | 📐 Çözünürlük: {v_info['width']}x{v_info['height']}")
            else:
                st.warning("Lütfen düzenlemek için bir video yükleyin.")

    with col_settings:
        st.subheader("⚙️ Düzenleme & Efekt Ayarları")

        # Trim
        st.markdown("**✂️ Kırpma (Trim):**")
        c_t1, c_t2 = st.columns(2)
        start_t = c_t1.number_input("Başlangıç (sn)", min_value=0.0, value=0.0, step=0.5)
        end_t = c_t2.number_input("Bitiş (sn, 0 = Tamamı)", min_value=0.0, value=0.0, step=0.5)

        # Aspect & Layout
        st.markdown("**📐 Format & Yerleşim:**")
        c_a1, c_a2 = st.columns(2)
        aspect = c_a1.selectbox("Format", ["9:16 (Shorts/TikTok/Reels)", "16:9 (YouTube Standard)", "Orijinal"])
        aspect_code = "9:16" if "9:16" in aspect else ("16:9" if "16:9" in aspect else "original")

        layout_choice = c_a2.selectbox(
            "Yerleşim Modu (9:16 İçin)",
            ["Bulanık Arka Plan + Ortalanmış Gameplay", "Merkez Kırpma (Zoom/Center Crop)", "Siyah Çerçeveli Sığdırma"]
        )
        layout_mode = "blur_background" if "Bulanık" in layout_choice else ("crop" if "Merkez" in layout_choice else "fit")

        # Visual Filters
        st.markdown("**🎨 Görsel İyileştirme & Filtreler:**")
        c_f1, c_f2, c_f3 = st.columns(3)
        contrast = c_f1.slider("Kontrast", 0.8, 1.5, 1.15, 0.05)
        saturation = c_f2.slider("Doygunluk", 0.8, 1.8, 1.30, 0.05)
        speed = c_f3.selectbox("Hız", [1.0, 0.5, 1.25, 1.5], index=0)
        vignette = st.checkbox("Vinyet Efekti (Odak Karartması)", value=True)

        # Text Overlays
        st.markdown("**✍️ Metin & Kanca Ekleme:**")
        hook_text = st.text_input("Üst Kanca Yazısı (Banner)", value="SONUNA KADAR İZLE! 🔥")
        wm_text = st.text_input("Alt Filigran / İsim", value=profile.get("watermark_text", "@GamerStudio"))

        # Audio Mixing
        st.markdown("**🎵 Ses & Müzik:**")
        uploaded_bgm = st.file_uploader("Arka Plan Müziği (Opsiyonel)", type=["mp3", "wav"])
        bgm_path = None
        if uploaded_bgm:
            bgm_path = str(AUDIO_DIR / uploaded_bgm.name)
            with open(bgm_path, "wb") as f:
                f.write(uploaded_bgm.read())

        c_v1, c_v2 = st.columns(2)
        gameplay_vol = c_v1.slider("Oyun Sesi", 0.0, 2.0, 1.0, 0.1)
        bgm_vol = c_v2.slider("Müzik Sesi", 0.0, 1.0, 0.25, 0.05)

        # Process Button
        if st.button("🚀 Videoyu İşle & Oluştur", use_container_width=True):
            if not video_input_path:
                st.error("Lütfen önce bir video seçin.")
            else:
                with st.spinner("Video FFmpeg motorunda işleniyor, filtreler ve efektler uygulanıyor..."):
                    try:
                        out_name = f"edited_{Path(video_input_path).stem}.mp4"
                        final_out = video_engine.process_video(
                            input_path=video_input_path,
                            output_filename=out_name,
                            start_time=start_t,
                            end_time=end_t if end_t > 0 else None,
                            target_aspect_ratio=aspect_code,
                            layout_mode=layout_mode,
                            contrast=contrast,
                            saturation=saturation,
                            enable_vignette=vignette,
                            speed_factor=speed,
                            hook_text=hook_text,
                            watermark_text=wm_text,
                            bgm_path=bgm_path,
                            bgm_volume=bgm_vol,
                            gameplay_volume=gameplay_vol
                        )
                        st.session_state.processed_video_path = final_out
                        st.success("✅ Video başarıyla oluşturuldu!")
                        st.video(final_out)
                    except Exception as e:
                        st.error(f"Hata oluştu: {e}")

# Session State Initialization
if "processed_video_path" not in st.session_state:
    st.session_state.processed_video_path = None
if "content_package" not in st.session_state:
    st.session_state.content_package = None
if "generated_thumbnail_path" not in st.session_state:
    st.session_state.generated_thumbnail_path = None
# ----------------- TAB 2: AI CONTENT & HOOKS -----------------
with tab2:
    st.header("🤖 AI İçerik, Başlık, Açıklama ve Etiket Üretici")
    st.write("Marketingskills algoritmalarına göre her platformun dinamiğine uygun viral içerikler oluşturun.")

    c_g1, c_g2 = st.columns([1, 1])
    with c_g1:
        game_name_input = st.text_input("Oyun Adı", value="Valorant")
        gameplay_desc_input = st.text_area(
            "Gameplay'de Ne Oluyor? (Özet / Olay)",
            value="1v5 clutch pozisyonunda son saniyede spike'ı çözerek inanılmaz bir ace atıyoruz.",
            height=120
        )
        ai_provider_choice = st.selectbox(
            "Yapay Zeka Motoru",
            ["gemini (Gemini 2.5 Flash)", "openai (GPT-4o-mini)", "anthropic (Claude 3.5)", "offline (Dahili Akıllı Üretici)"]
        )
        provider_key = ai_provider_choice.split(" ")[0]

        if st.button("✨ Tüm Platformlar İçin İçerik Üret", use_container_width=True):
            with st.spinner("Platform algoritmalarına uygun başlıklar ve açıklamalar hazırlanıyor..."):
                pkg = content_engine.generate_full_package(
                    game_name=game_name_input,
                    gameplay_description=gameplay_desc_input,
                    provider=provider_key
                )
                st.session_state.content_package = pkg
                st.success("Tüm platform paketleri başarıyla oluşturuldu!")

    with c_g2:
        st.subheader("💡 Hazır Kanca (Viral Hook) Kütüphanesi")
        hook_cat = st.selectbox("Kategori Seç:", ["shock_and_hype", "curiosity", "skill_and_value", "story_and_journey"])
        hooks = VIRAL_GAMING_HOOKS.get(hook_cat, [])
        for h in hooks:
            st.code(h, language="text")

    # Display generated content tabs if ready
    if st.session_state.content_package:
        pkg = st.session_state.content_package
        st.divider()
        st.subheader("📋 Üretilen İçerikler (İncele & Düzenle)")

        p_tab_yt, p_tab_tk, p_tab_ig, p_tab_x = st.tabs(["🔴 YouTube", "⬛ TikTok", "📸 Instagram", "🐦 X (Twitter)"])

        with p_tab_yt:
            yt_data = pkg.get("youtube", {})
            st.markdown("**Seçilen Başlık (CTR Optimized):**")
            st.text_input("YouTube Başlığı", value=yt_data.get("selected_title", ""), key="yt_title_input")
            st.markdown("**Açıklama (Description):**")
            st.text_area("YouTube Açıklaması", value=yt_data.get("description", ""), height=150, key="yt_desc_input")
            c_tag1, c_tag2 = st.columns(2)
            c_tag1.text_input("Arama Etiketleri (Tags)", value=", ".join(yt_data.get("tags", [])))
            c_tag2.text_input("Hashtagler", value=" ".join(yt_data.get("hashtags", [])))

        with p_tab_tk:
            tk_data = pkg.get("tiktok", {})
            st.text_input("0-3s Kanca Yazısı", value=tk_data.get("hook_text", ""), key="tk_hook_input")
            st.text_area("TikTok Açıklaması (<150 karakter odaklı)", value=tk_data.get("caption", ""), height=100, key="tk_cap_input")
            st.text_input("TikTok Hashtagleri", value=" ".join(tk_data.get("hashtags", [])))

        with p_tab_ig:
            ig_data = pkg.get("instagram", {})
            st.text_area("Reels Açıklaması & Çağrı", value=ig_data.get("caption", ""), height=120, key="ig_cap_input")
            st.text_input("Instagram Hashtagleri", value=" ".join(ig_data.get("hashtags", [])))

        with p_tab_x:
            x_data = pkg.get("x", {})
            st.text_area("X / Tweet Metni (İlk 8 kelime kancalı)", value=x_data.get("tweet", ""), height=100, key="x_tweet_input")
            st.text_input("X Hashtagleri", value=" ".join(x_data.get("hashtags", [])))

# ----------------- TAB 3: THUMBNAIL STUDIO -----------------
with tab3:
    st.header("🖼️ Gamer Thumbnail & Kapak Stüdyosu")
    st.write("Gameplay anından yüksek çözünürlüklü kare çekin, büyük gamer başlığı ve dikkat çekici rozetler ekleyin.")

    c_th1, c_th2 = st.columns([1, 1])
    with c_th1:
        thumb_source = st.session_state.processed_video_path or (str(list(INPUTS_DIR.glob("*.mp4"))[0]) if list(INPUTS_DIR.glob("*.mp4")) else None)
        if thumb_source:
            st.info(f"Kullanılan Video: {Path(thumb_source).name}")
            t_sec = st.slider("Kare Zamanı (Saniye)", min_value=0.0, max_value=60.0, value=2.0, step=0.5)
            t_title = st.text_input("Thumbnail Başlık Yazısı", value="1000 IQ CLUTCH!")
            t_badge = st.text_input("Köşe Rozet Yazısı", value="INSANE")
            t_aspect = st.selectbox("Thumbnail Formatı", ["16:9 (YouTube Yatay)", "9:16 (Shorts/Reels Dikey)"])
            t_aspect_code = "16:9" if "16:9" in t_aspect else "9:16"
            t_border = st.color_picker("Çerçeve Rengi", "#FF0055")

            if st.button("🎨 Thumbnail Oluştur", use_container_width=True):
                with st.spinner("Thumbnail hazırlanıyor..."):
                    thumb_path = thumbnail_engine.generate_thumbnail_from_video(
                        video_path=thumb_source,
                        timestamp_sec=t_sec,
                        title_text=t_title,
                        badge_text=t_badge,
                        aspect_ratio=t_aspect_code,
                        output_filename=f"thumb_{Path(thumb_source).stem}.jpg",
                        border_color=t_border
                    )
                    st.session_state.generated_thumbnail_path = thumb_path
                    st.success("✅ Thumbnail hazırlandı!")
        else:
            st.warning("Thumbnail çıkarmak için lütfen önce bir video seçin veya işleyin.")

    with c_th2:
        if st.session_state.generated_thumbnail_path and Path(st.session_state.generated_thumbnail_path).exists():
            st.subheader("Önizleme:")
            st.image(st.session_state.generated_thumbnail_path, use_container_width=True)
            with open(st.session_state.generated_thumbnail_path, "rb") as file:
                st.download_button("💾 Thumbnail İndir", data=file, file_name=Path(st.session_state.generated_thumbnail_path).name, mime="image/jpeg", use_container_width=True)
            
            st.divider()
            st.markdown("**🎨 Midjourney / DALL-E / Flux İçin AI Görsel Promptu:**")
            ai_p = thumbnail_engine.generate_ai_thumbnail_prompt(video_title=t_title if 't_title' in locals() else "Epic Clutch", game_name=game_name_input if 'game_name_input' in locals() else "Valorant")
            st.code(ai_p, language="text")

# ----------------- TAB 4: SOCIAL PUBLISHER & EXPORT -----------------
with tab4:
    st.header("🚀 Çoklu Platform Paylaşım & Hazır Dağıtım Paketi")
    st.write("Tek tıkla YouTube, X (Twitter), TikTok ve Instagram için tüm dosyaları paketleyin veya doğrudan paylaşın.")

    vid_target = st.session_state.processed_video_path
    if not vid_target and list(OUTPUTS_DIR.glob("*.mp4")):
        vid_target = str(list(OUTPUTS_DIR.glob("*.mp4"))[0])

    if vid_target and st.session_state.content_package:
        st.success(f"🎯 Paylaşıma Hazır Video: {Path(vid_target).name}")

        col_b1, col_b2 = st.columns([1, 1])

        with col_b1:
            st.subheader("📦 1-Tık Dağıtım Paketi Oluştur")
            st.write("Tüm platformlar için video, thumbnail, açıklama metinleri ve etiketleri tek bir klasörde toplar.")
            bundle_name = st.text_input("Paket / Klasör Adı", value=f"export_{Path(vid_target).stem}")

            if st.button("🎁 Dağıtım Paketini Oluştur", use_container_width=True):
                bundle_path = social_publisher.create_export_bundle(
                    bundle_name=bundle_name,
                    video_path=vid_target,
                    thumbnail_path=st.session_state.generated_thumbnail_path,
                    content_package=st.session_state.content_package
                )
                st.success(f"✅ Paket hazırlandı: {bundle_path}")
                agent_memory.record_video({
                    "video_file": Path(vid_target).name,
                    "bundle": bundle_name,
                    "youtube_title": st.session_state.content_package.get("youtube", {}).get("selected_title")
                })

        with col_b2:
            st.subheader("🌐 Doğrudan API ile Paylaş")

            st.markdown("**🔴 YouTube:**")
            if st.button("Upload to YouTube", use_container_width=True):
                yt_res = social_publisher.publish_to_youtube(
                    video_path=vid_target,
                    title=st.session_state.content_package.get("youtube", {}).get("selected_title", "Gameplay"),
                    description=st.session_state.content_package.get("youtube", {}).get("description", ""),
                    tags=st.session_state.content_package.get("youtube", {}).get("tags", []),
                    thumbnail_path=st.session_state.generated_thumbnail_path
                )
                st.info(yt_res["message"])

            st.markdown("**🐦 X (Twitter):**")
            if st.button("Tweet to X", use_container_width=True):
                tw_text = st.session_state.content_package.get("x", {}).get("tweet", "")
                tw_tags = " ".join(st.session_state.content_package.get("x", {}).get("hashtags", []))
                x_res = social_publisher.publish_to_x(tweet_text=f"{tw_text} {tw_tags}", video_path=vid_target)
                st.info(x_res["message"])

            st.markdown("**⬛ TikTok & 📸 Instagram:**")
            st.caption("TikTok Content Posting & Instagram Reels modülleri aktif. Hesap tokeni girildiğinde otomatik yüklenir.")
    else:
        st.warning("Paylaşım yapabilmek veya paket oluşturabilmek için lütfen önce 1. Sekmede videoyu işleyin ve 2. Sekmede içerik üretin.")

# ----------------- TAB 5: AGENT MEMORY & HISTORY -----------------
with tab5:
    st.header("🧠 Ajan Hafızası (Persistent Context) & Geçmiş")
    st.write("Kanalınızın geçmiş videoları, performans tercihleri ve yapay zeka hafıza durumu.")

    hist = agent_memory.load_history()
    if hist:
        st.subheader("📜 Son İşlenen Videolar")
        for item in hist:
            with st.expander(f"🎬 {item.get('video_file', 'Video')} - {item.get('timestamp', '')[:19]}"):
                st.write(f"**Başlık:** {item.get('youtube_title', 'N/A')}")
                st.write(f"**Paket Adı:** {item.get('bundle', 'N/A')}")
    else:
        st.info("Henüz işlenmiş video geçmişi kaydedilmedi.")

    st.divider()
    st.subheader("⚙️ API Anahtarları ve Ortam Değişkenleri (.env)")
    st.write("API anahtarlarınızı `.env` dosyasına kaydederek doğrudan kullanabilirsiniz:")
    st.code("""
# .env dosyası içeriği:
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_claude_api_key_here
X_API_KEY=your_x_api_key
X_ACCESS_TOKEN=your_x_access_token
TIKTOK_ACCESS_TOKEN=your_tiktok_token
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
""", language="properties")

