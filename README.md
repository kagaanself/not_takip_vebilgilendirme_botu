# 🎓 KTÜN OBS Not Takip & Telegram Bildirim Botu

Bu proje, **Konya Teknik Üniversitesi (KTÜN)** öğrencilerinin notlarını otomatik takip eden bir Python botudur.

## 🛠️ Temel Özellikler

* **Otomatik Giriş:** Şifrelerinizi güvenle kullanır.
* **Anlık Bildirim:** Not girildiğinde Telegram'dan mesaj atar.
* **Veritabanı:** Notları hafızasında tutar, sadece yenileri haber verir.

## 🚀 Kurulum

### 1. Gereksinimler

* Python 3.8+
* Google Chrome
* ChromeDriver (Selenium 4 ile otomatik kurulur)

### 2. Kütüphane Kurulumu

```bash
pip install -r requirements.txt
```

### 3. Ayarlar

`.env.example` dosyasını `.env` yapın ve içini doldurun:

```env
STUDENT_NO=okul_numaraniz
PASSWORD=obs_sifreniz
TELEGRAM_TOKEN=bot_tokeniniz
TELEGRAM_CHAT_ID=chat_id_numaraniz
```

## 💻 Kullanım

Botu başlatmak için:

```bash
python not_takip_botu.py
```

## 📁 Dosya Yapısı

* `not_takip_botu.py` : Ana Kod
* `.env.example` : Ayar Şablonu
* `requirements.txt` : Kütüphaneler

---

**Geliştiren:** [@kagaanself](https://github.com/kagaanself)
