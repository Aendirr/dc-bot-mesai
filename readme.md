# 🚀 Mesai Discord Botu (Slash Command)

Discord sunucularında kullanıcıların mesai giriş-çıkışlarını takip eden, buton tabanlı ve `/` komutlarıyla çalışan bir bottur.

---

## ✨ Özellikler

* Slash command (`/`) sistemi
* Buton ile mesai giriş / çıkış
* JSON tabanlı veri saklama (`data.json`)
* Toplam mesai süresi hesaplama
* Günlük ve haftalık mesai takibi
* Mesai sıralaması
* Log kanalı desteği
* Bot restart sonrası veri kaybı yok

---

## 📁 Proje Yapısı

```
mesai-bot/
├─ bot.py
├─ config.py
├─ store.py
├─ utils.py
└─ data.json
```

---

## ⚙️ Kurulum

### 1. Python kurulumu

Python 3.10+ önerilir

Kontrol:

```
python --version
```

---

### 2. Gerekli paketleri kur

```
pip install -U discord.py
```

---

### 3. Config ayarları

`config.py` dosyasını aç ve doldur:

```python
TOKEN = "BOT_TOKEN_BURAYA"
GUILD_ID = 123456789012345678
LOG_CHANNEL_ID = 123456789012345678
DATA_FILE = "data.json"
```

---

## 🤖 Discord Developer Ayarları

### 1. Bot oluştur

* https://discord.com/developers/applications
* **New Application**
* **Bot → Add Bot**

---

### 2. Token al

* Bot sekmesi → **Reset Token**
* `config.py` içine yapıştır

---

### 3. Botu sunucuya ekle

**OAuth2 → URL Generator**

Seç:

#### Scopes

* ✅ `bot`
* ✅ `applications.commands`

#### Bot Permissions

* ✅ Send Messages
* ✅ Embed Links
* ✅ Use Slash Commands

Oluşan linki aç → sunucuya ekle

---

## ▶️ Botu Çalıştırma

Terminal:

```
python bot.py
```

Başarılıysa:

```
Giriş yapıldı: BotAdı
Slash komut sayısı: X
```

---

## 🧠 Kullanım

### 📌 Panel oluştur

```
/panel
```

⚠️ Sadece **Sunucuyu Yönet (Manage Guild)** yetkisi olan kullanabilir

Bu komut kanala butonlu panel gönderir:

* ✅ Mesai Gir
* ❌ Mesaiden Çık

---

### 📊 Kendi mesai durumun

```
/durum
```

---

### 🏆 Mesai sıralaması

```
/liste
```

---

### 👤 Başkasının mesaisine bak

```
/bak @kullanici
```

---

## 🧾 Veri Yapısı (data.json)

Örnek:

```json
{
  "users": {
    "123456789": {
      "username": "kullanici",
      "user_id": 123456789,
      "total_seconds": 5000,
      "active": false,
      "started_at": null,
      "last_end_at": "2026-04-02T12:00:00",
      "sessions": [
        {
          "start": "...",
          "end": "...",
          "duration_seconds": 1200
        }
      ]
    }
  }
}
```

---

## 🪵 Log Sistemi

Mesai giriş/çıkışları belirli kanala gönderilir.

### Kanal ID alma:

1. Discord → Ayarlar → Gelişmiş → **Developer Mode aç**
2. Kanala sağ tık → **ID kopyala**
3. `LOG_CHANNEL_ID` içine yapıştır

---

## ⚠️ Önemli Notlar

* Bot otomatik mesaj atmaz → `/panel` komutu gerekir
* Slash komutlar bazen 1-2 dk gecikebilir
* Bot restart olsa bile veriler korunur
* Aynı anda birden fazla mesai başlatılamaz

---

## 🔧 Sorun Giderme

### Komutlar görünmüyor

* Botu restart et
* 1-2 dk bekle

---

### Bot mesaj atmıyor

* Yetkileri kontrol et:

  * Send Messages
  * Embed Links

---

### data.json oluşmadı

* Botu en az 1 kere çalıştır

---

## 🧩 Geliştirme Fikirleri

* Mesai sıfırlama komutu
* Günlük rapor sistemi
* Web panel (React + API)
* SQLite / PostgreSQL geçiş
* Multi-server destek

---

## 📌 Özet

1. Botu oluştur
2. Token al
3. Botu sunucuya ekle
4. `python bot.py` çalıştır
5. Discord’da `/panel` yaz
6. Kullanmaya başla

---

## 👨‍💻 Not

Bu bot tamamen async yapıda çalışır ve `discord.py` kullanır.
Slash command sistemi `app_commands` ile yönetilir.

---
