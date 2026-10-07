# 🎮 GameFlow AI - Otomatik Gameplay Video Stüdyosu & Çoklu Platform Dağıtım Sistemi

GameFlow AI; ham gameplay videolarınızı otomatik olarak analiz eden, profesyonel efekt ve filtrelemelerle (9:16 Shorts/Reels/TikTok veya 16:9 YouTube formatında) dönüştüren, yapay zeka ile platformlara özel viral başlıklar, açıklamalar ve etiketler üreten, dikkat çekici thumbnail (kapak görseli) hazırlayan ve **YouTube, X (Twitter), TikTok ve Instagram** platformlarında paylaşıma hazır hale getiren uçtan uca otonom bir stüdyo sistemidir.

---

## 📚 Entegre Edilen Açık Kaynak Repolar ve Kullanım Alanları

Projenin geliştirilmesinde sağladığınız repolardan doğrudan yararlanılan mimariler ve teknikler:

1. **`coreyhaines31/marketingskills`**:
   - **Kullanım:** Sosyal medya algoritma kuralları ve kanca kütüphanesi (`short-form-video.md`, `x-algorithm.md`, `platform-limits.md`).
   - YouTube için yüksek CTR (%10+) başlık ve açıklama stratejileri.
   - TikTok için 0-3 saniyelik görsel kanca ve ilk 150 karakter odaklı açıklama sınırları.
   - X (Twitter) için Grox/Phoenix algoritmasına uygun ilk 8 kelimede iddia, ilk 10 kelimede oyun adı ve 280 karakter optimizasyonu.
   - Instagram Reels için kaydetme ve paylaşma odaklı çağrılar.

2. **`thedotmack/claude-mem` & `addyosmani/agent-skills`**:
   - **Kullanım:** Kalıcı ajan hafızası (`gameflow/core/memory.py`).
   - Yayıncının kanal adı, oyun alanı (niche), dil tercihi (TR/EN), içerik tonu, filigranı ve geçmiş video kayıtları bellekte tutulur ve LLM promptlarına otomatik aktarılır.

3. **`google/eng-practices`**:
   - **Kullanım:** Temiz kod yapısı, bağımsız modüller (`video_engine`, `content_engine`, `thumbnail_engine`, `social_publisher`) ve kapsamlı entegrasyon testleri (`test_pipeline.py`).

4. **`anthropics/claude-quickstarts` & `luongnv89/claude-howto`**:
   - **Kullanım:** Çoklu yapay zeka sağlayıcısı desteği (Google Gemini 2.5 Flash, Claude 3.5, OpenAI GPT-4o ve dahili akıllı çevrimdışı motor).

---

## 🚀 Temel Özellikler

### 🎯 AI Kill & Aksiyon Avcısı (`highlight_detector.py`)
- **Uzun Videolardan Otomatik Klip Çıkarma:** 10 dakika, 30 dakika veya 1 saatlik uzun gameplay videolarınızı saniyeler içinde tarar.
- **Akıllı Kill / Hype Tespiti:** Silah patlamaları, haykırışlar, spiker sesleri ("Double Kill", "Ace"), ses desibel sıçramaları ve ani aksiyon anlarını milisaniye hassasiyetiyle yakalar.
- **Dinamik Klip Süreleri:** 5 saniye kısıtı yoktur! Pozisyon 15 saniye sürdüyse 15s, 28 saniyelik clutch ise 28s olarak doğal uzunluğunda keser.
- **Akıllı Ön-Pay (Pre-roll) & Son-Pay (Post-roll):** Kill anından önce (örn. 4-5 saniye) pusu/nişan alma hazırlığını, vuruştan sonra (örn. 3-4 saniye) killfeed ve sevinç anını otomatik dahil eder.
- **Combo & Multi-Kill Birleştirme:** Birbirine yakın gerçekleşen peş peşe vuruşları (Ace / Clutch) tek bir epik klipte otomatik birleştirir.


### 1. 🎬 Video Stüdyosu (`video_engine.py`)
- **Akıllı Kırpma (Trim):** Başlangıç ve bitiş saniyelerine göre kayıpsız kesme.
- **Format Dönüştürücü:**
  - `9:16 Dikey (Shorts / TikTok / Reels)`: Pro oyuncu tarzı **Bulanık Arka Plan + Ortalanmış Net Gameplay** (arka plan 9:16 bulanıklaştırılır, ortada orijinal net oyun akar), Merkez Kırpma veya Sığdırma.
  - `16:9 Yatay`: YouTube ana video formatı.
- **Görsel İyileştirme:** Kontrast, Doygunluk artırma, Odak Vinyeti (Vignette) ve Hız ayarı (0.5x Slow-mo, 1.25x Hızlandırma).
- **Yazı & Kanca Katmanları:** Üst kanca başlığı (`SONUNA KADAR İZLE!`) ve alt filigran/kanal etiketi (`@GamerStudio`).
- **Ses & Müzik Miksajı:** Oyun sesi ve arka plan müziğini (BGM) ayarlanabilir ses seviyeleriyle miksleme.

### 2. 🤖 AI İçerik & Viral Metin Üretici (`content_engine.py`)
- YouTube, TikTok, Instagram ve X için özel formatlanmış içerik:
  - **YouTube:** 3 farklı viral başlık alternatifi, SEO açıklaması, arama etiketleri ve hashtagler.
  - **TikTok:** 3 saniyelik ekranda beliren metin, <150 karakter kanca açıklaması ve 4 hedef hashtag.
  - **Instagram Reels:** Etkileşim sorusu, çağrı ve popüler etiketler.
  - **X (Twitter):** İlk 8 kelimede kanca, 1-2 hashtag ve <280 karakter tweet.

### 3. 🖼️ Gamer Thumbnail Stüdyosu (`thumbnail_engine.py`)
- Gameplay videosundan istenen saniyede yüksek çözünürlüklü kare çıkarma.
- Kontrast, doygunluk ve keskinlik artırma.
- Kalın siyah konturlu (stroke) parlak sarı/kırmızı gamer yazı stili.
- Sol üst dikkat çekici rozetler (`INSANE`, `1v5 ACE`, `1000 IQ`, `VICTORY`).
- Neon kenarlık çerçevesi (16:9 veya 9:16 formatlarında).
- Midjourney / DALL-E / Flux için hazır AI görsel promptu üretimi.

### 4. 🌐 Çoklu Platform Dağıtım & 1-Tık Paketleme (`social_publisher.py`)
- **1-Tık Dağıtım Paketi:** Videoyu, thumbnail'ı ve her platformun kopyalanmaya hazır metin dosyalarını (`youtube.txt`, `tiktok.txt`, `instagram.txt`, `twitter_x.txt`, `bundle_manifest.json`) tek klasörde toplar.
- **Doğrudan API Desteği:** YouTube Data API v3, X API v2, TikTok Posting API ve Instagram Graph API hazır entegrasyonları.

---

## 🛠️ Nasıl Çalıştırılır?

### Arayüzü Başlatma (Streamlit Web Dashboard)
Masaüstündeki çalışma klasöründe yer alan **`run_app.bat`** dosyasına çift tıklayabilir veya terminalden şu komutu verebilirsiniz:

```bash
python -m streamlit run app.py
```

Tarayıcınızda `http://localhost:8501` adresi açılacaktır.

### Komut Satırından Çalıştırma (CLI)
Tam otomatik işlem (Video düzenleme + AI içerik + Thumbnail + Dağıtım paketi):

```bash
python cli.py auto --video "video_yolu.mp4" --game "Valorant" --desc "1v5 clutch with Vandal on Haven" --aspect 9:16
```

Uzun videodaki kill ve aksiyon anlarını otomatik tespit etme:
```bash
python cli.py detect --video "uzun_video.mp4"
```

Uzun videodaki tüm kill anlarını tek komutla tespit edip 9:16 Shorts olarak kesme ve paketleme:
```bash
python cli.py auto-highlights --video "uzun_video.mp4" --game "Valorant" --aspect 9:16
```


Sadece içerik üretimi:
```bash
python cli.py content --game "CS2" --desc "Dust 2 AWP ace"
```

Sadece thumbnail üretimi:
```bash
python cli.py thumbnail --video "video_yolu.mp4" --time 2.5 --title "1000 IQ CLUTCH!"
```

---

## 🧪 Testlerin Çalıştırılması

Tüm sistemin sorunsuz çalıştığını doğrulamak için:

```bash
python test_pipeline.py
```
