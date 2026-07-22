# Startgate Telemetry API Servisi

Oyun içi telemetri verilerini (oyuncu hareketleri, oturum bilgileri vb.) toplayan, Pydantic ile doğrulayan, SQLAlchemy ORM ve SQLite ile kalıcı olarak saklayan yüksek performanslı bir backend API servisidir.

## 🛠️ Tech Stack (Kullanılan Teknolojiler)

- **Dil:** Python 3.11+
- **Web Çatısı:** FastAPI + Uvicorn
- **Veri Doğrulama:** Pydantic
- **Veritabanı & ORM:** SQLite, SQLAlchemy ORM
- **Versiyon Kontrolü:** Git & GitHub

## 📁 Proje Mimarisi

```text
startgate-telemetry-api/
│
├── app/                  # Kaynak kodlar
│   ├── __init__.py
│   ├── database.py       # Veritabanı bağlantı ayarları
│   ├── main.py           # FastAPI uygulaması ve API uç noktaları
│   ├── models.py         # SQLAlchemy Veritabanı Modelleri (ORM)
│   └── schemas.py        # Pydantic Veri Doğrulama Modelleri
│
├── reports/              # Haftalık staj durum raporları
├── tests/                # Test dosyaları (pytest)
├── telemetry.db          # SQLite veritabanı dosyası
├── requirements.txt      # Proje bağımlılıkları
└── README.md

🚀 Kurulum ve Çalıştırma Rehberi
Projeyi kendi bilgisayarında çalıştırmak için aşağıdaki adımları takip edebilirsin.

1. Depoyu Klonlayın:
git clone https://github.com/gokalpdasdelen02-ui/startgate-telemetry-api.git
cd startgate-telemetry-api

2. Sanal Ortam Oluşturun ve Aktif Edin:

macOS / Linux için:
python3 -m venv venv
source venv/bin/activate

Windows için:
python -m venv venv
venv\Scripts\activate

3. Gerekli Kütüphaneleri Yükleyin:
pip install -r requirements.txt

4. Yerel Sunucuyu Ayağa Kaldırın:
uvicorn app.main:app --reload

Sunucu başarıyla çalıştığında terminalde Uvicorn running on [http://127.0.0.1:8000](http://127.0.0.1:8000) mesajını göreceksiniz.

🧪 API Test Etme ve Dokümantasyon
FastAPI, otomatik olarak interaktif bir test arayüzü (Swagger UI) oluşturur. Proje çalışırken tarayıcından şu adrese gidebilirsin:

👉 http://127.0.0.1:8000/docs

Bu arayüz üzerinden:

POST /events uç noktasına örnek JSON verileri göndererek veritabanı kayıt işlemlerini test edebilir,

GET /health uç noktası ile servisin durumunu kontrol edebilirsiniz.
```
