# Startgate Telemetry API Servisi

Oyunlardan gelen telemetri olaylarını kabul eden, doğrulayan, veritabanında saklayan ve sorgulanabilir hâle getiren bir backend API servisidir.

API’ye gönderilen veriler Pydantic şemalarıyla doğrulanır. Geçerli olaylar SQLAlchemy ORM aracılığıyla SQLite veritabanına kaydedilir. Kaydedilen olaylar genel olarak veya kullanıcı kimliğine göre sayfalı şekilde sorgulanabilir.

## Özellikler

- Servis durumunu kontrol eden sağlık endpointi
- Tek bir telemetri olayını doğrulayıp kaydetme
- Tek istekte 1–100 olay kaydeden batch endpointi
- Pydantic ile veri tipi ve alan doğrulaması
- Olay kategorisi ile `event_data` içeriği arasında eşleşme kontrolü
- Katı alan doğrulaması ve fazla alanların reddedilmesi
- SQLAlchemy ORM ve SQLite ile kalıcı veri saklama
- Veritabanı hatalarında transaction rollback işlemi
- Genel olay listeleme
- Kullanıcı kimliğine göre olay listeleme
- `skip` ve `limit` parametreleriyle sayfalama
- Olay kategorisine göre filtreleme
- Başlangıç ve bitiş tarihine göre filtreleme
- Günlük olay sayılarını döndüren istatistik endpointi
- Tarih aralığına göre benzersiz aktif kullanıcı sayısı
- API key ile korunan event ve istatistik endpointleri
- Loguru ile yapılandırılmış uygulama logları
- Terminal için okunabilir, dosya için JSON log çıktısı
- Pydantic response modelleriyle standart API cevapları
- Swagger/OpenAPI dokümantasyonu
- pytest ile otomatik API testleri
- pytest-cov ile test kapsam raporu
- UTC tabanlı olay zamanı yönetimi
- `.env` dosyasıyla gizli yapılandırma yönetimi

## Kullanılan Teknolojiler

- **Dil:** Python 3.11+
- **Web çatısı:** FastAPI
- **ASGI sunucusu:** Uvicorn
- **Veri doğrulama:** Pydantic
- **ORM:** SQLAlchemy
- **Veritabanı:** SQLite
- **Kod biçimlendirme:** Black
- **Versiyon kontrolü:** Git ve GitHub
- **Ortam değişkenleri:** python-dotenv
- **Test:** pytest, HTTPX TestClient
- **Test kapsamı:** pytest-cov
- **Loglama:** Loguru

## Proje Mimarisi

```text
startgate-telemetry-api/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI uygulamasının başlangıç noktası
│   ├── database.py             # Veritabanı bağlantısı ve session yönetimi
│   ├── logging_config.py       # Loguru terminal ve JSON log ayarları
│   ├── models.py               # SQLAlchemy veritabanı modeli
│   ├── schemas.py              # Pydantic giriş ve cevap şemaları
│   ├── security.py             # API key doğrulaması
│   ├── settings.py             # Ortam değişkenleri ve uygulama ayarları
│   │
│   └── routers/
│       ├── __init__.py
│       ├── events.py           # Event oluşturma, batch ve sorgu endpointleri
│       └── stats.py            # Günlük olay ve aktif kullanıcı istatistikleri
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Test veritabanı ve ortak pytest fixtureları
│   ├── test_events.py          # Event, batch ve filtreleme testleri
│   ├── test_health.py          # Sağlık endpointi testleri
│   ├── test_pagination.py      # Sayfalama testleri
│   ├── test_stats.py           # İstatistik endpointi testleri
│   └── test_validation.py      # Pydantic doğrulama testleri
│
├── docs/
│   └── veritabani-semasi.md
│
├── reports/
│   └── hafta-1.md
│
├── .env.example               # Örnek ortam değişkenleri
├── .gitignore
├── api-tasarimi.md
├── requirements.txt           # Uygulama bağımlılıkları
├── requirements-dev.txt       # Test ve geliştirme bağımlılıkları
└── README.md
```

### Dosyaların Görevleri

- `app/main.py`: FastAPI uygulamasını oluşturur, loglama ayarlarını başlatır ve routerları uygulamaya bağlar.
- `app/database.py`: SQLAlchemy engine, session factory, temel model sınıfı ve veritabanı dependency’sini tanımlar.
- `app/logging_config.py`: Terminal için okunabilir, dosya için JSON biçiminde Loguru loglarını yapılandırır.
- `app/models.py`: Veritabanındaki `game_events` tablosunu temsil eden SQLAlchemy modelini içerir.
- `app/schemas.py`: Event verilerini, batch isteklerini, filtre ve istatistik cevaplarını doğrulayan Pydantic modellerini içerir.
- `app/security.py`: `X-API-Key` headerını alır, güvenli biçimde doğrular ve başarısız girişleri loglar.
- `app/settings.py`: `.env` ve ortam değişkenlerinden uygulama ayarlarını yükler.
- `app/routers/events.py`: Tek event oluşturma, batch kayıt, genel sorgulama, filtreleme, sayfalama ve kullanıcıya göre sorgulama endpointlerini içerir.
- `app/routers/stats.py`: Günlük event sayıları ve benzersiz aktif kullanıcı istatistiklerini döndüren endpointleri içerir.
- `tests/conftest.py`: Geçici SQLite test veritabanını, TestClient nesnesini ve ortak pytest fixturelarını oluşturur.
- `tests/test_events.py`: Event oluşturma, API key, batch, kategori ve tarih filtreleme testlerini içerir.
- `tests/test_health.py`: Sağlık endpointinin testini içerir.
- `tests/test_pagination.py`: Genel ve kullanıcıya özel sayfalama davranışlarını test eder.
- `tests/test_stats.py`: Günlük event ve aktif kullanıcı istatistiklerini test eder.
- `tests/test_validation.py`: Pydantic alan, veri tipi ve kategori-model eşleşme doğrulamalarını test eder.
- `docs/veritabani-semasi.md`: Veritabanı kolonlarını ve tasarım kararlarını açıklar.
- `api-tasarimi.md`: Endpointleri, veri şemalarını ve doğrulama kurallarını belgeler.
- `requirements.txt`: Uygulamanın çalışması için gereken bağımlılıkları içerir.
- `requirements-dev.txt`: pytest, pytest-cov ve HTTPX gibi test/geliştirme bağımlılıklarını içerir.

## Kurulum

### 1. Depoyu klonlama

```bash
git clone https://github.com/gokalpdasdelen02-ui/startgate-telemetry-api.git
cd startgate-telemetry-api
```

### 2. Sanal ortam oluşturma

```bash
python -m venv venv
source venv/bin/activate
```

Windows kullanılıyorsa:

```bash
venv\Scripts\activate
```

### 3. Uygulama bağımlılıklarını yükleme

```bash
python -m pip install -r requirements.txt
```

Testleri ve coverage raporunu da çalıştırmak için geliştirme bağımlılıklarını yükleyin:

```bash
python -m pip install -r requirements-dev.txt
```

### 4. Ortam değişkenlerini hazırlama

Örnek ortam dosyasını kopyalayın:

```bash
cp .env.example .env
```

`.env` dosyasında API anahtarını ve veritabanı bağlantısını tanımlayın:

```env
TELEMETRY_API_KEY=your-secret-api-key
DATABASE_URL=sqlite:///./telemetry.db
```

Gerçek API anahtarı içeren `.env` dosyası Git deposuna eklenmemelidir.

### 5. Uygulamayı çalıştırma

```bash
python -m uvicorn app.main:app --reload
```

Uygulama varsayılan olarak şu adreste çalışır:

```text
http://127.0.0.1:8000
```

Swagger arayüzü:

```text
http://127.0.0.1:8000/docs
```

ReDoc arayüzü:

```text
http://127.0.0.1:8000/redoc
```

Event ve istatistik endpointlerini kullanmak için isteklere şu header eklenmelidir:

```text
X-API-Key: your-secret-api-key
```

## API Endpointleri

Sağlık kontrolü dışındaki bütün event ve istatistik endpointleri `X-API-Key` headerı ile korunur.

| Metot  | Endpoint                 | Açıklama                                                                 | API key  |
| ------ | ------------------------ | ------------------------------------------------------------------------ | -------- |
| `GET`  | `/health`                | Servisin çalışıp çalışmadığını kontrol eder                              | Gerekmez |
| `POST` | `/events/`               | Tek bir telemetri eventini doğrular ve kaydeder                          | Gerekli  |
| `POST` | `/events/batch`          | Tek istekte 1–100 eventi doğrular ve kaydeder                            | Gerekli  |
| `GET`  | `/events/`               | Eventleri listeler; kategori, tarih ve pagination filtrelerini destekler | Gerekli  |
| `GET`  | `/events/user/{user_id}` | Belirtilen kullanıcıya ait eventleri listeler                            | Gerekli  |
| `GET`  | `/stats/daily-events`    | Eventleri günlere göre gruplandırarak toplam sayılarını döndürür         | Gerekli  |
| `GET`  | `/stats/active-users`    | Benzersiz aktif kullanıcı sayısını döndürür                              | Gerekli  |

### `GET /events/` sorgu parametreleri

| Parametre   | Tür      | Zorunlu | Açıklama                                                            |
| ----------- | -------- | ------- | ------------------------------------------------------------------- |
| `category`  | string   | Hayır   | Event kategorisine göre filtreleme yapar                            |
| `date_from` | datetime | Hayır   | Bu tarih ve sonrasındaki eventleri getirir                          |
| `date_to`   | datetime | Hayır   | Bu tarih ve öncesindeki eventleri getirir                           |
| `skip`      | integer  | Hayır   | Atlanacak kayıt sayısı; varsayılan değer `0`                        |
| `limit`     | integer  | Hayır   | Döndürülecek en fazla kayıt sayısı; varsayılan `10`, en fazla `100` |

Örnek:

```text
GET /events/?category=business&date_from=2026-08-01T00:00:00Z&date_to=2026-08-06T23:59:59Z&skip=0&limit=10
```

## API Key Doğrulaması

Sağlık kontrolü dışındaki event ve istatistik endpointleri geçerli bir API anahtarı gerektirir.

API anahtarı şu HTTP headerı içinde gönderilir:

```text
X-API-Key: your-secret-api-key
```

API anahtarı JSON istek gövdesine yazılmaz.

Swagger arayüzünde API anahtarını tanımlamak için sayfanın üst kısmındaki **Authorize** düğmesine basın. Anahtarın başına `Bearer` eklemeden yalnızca anahtar değerini girin.

### Endpointlerin erişim durumu

| Endpoint                     | API key gerekli mi? |
| ---------------------------- | ------------------- |
| `GET /health`                | Hayır               |
| `POST /events/`              | Evet                |
| `POST /events/batch`         | Evet                |
| `GET /events/`               | Evet                |
| `GET /events/user/{user_id}` | Evet                |
| `GET /stats/daily-events`    | Evet                |
| `GET /stats/active-users`    | Evet                |

API anahtarı eksik veya geçersiz olduğunda servis:

```text
401 Unauthorized
```

durum kodunu döndürür:

```json
{
  "detail": "Invalid or missing API key."
}
```

Sunucuda `TELEMETRY_API_KEY` yapılandırılmamışsa servis:

```text
500 Internal Server Error
```

durum kodunu döndürür:

```json
{
  "detail": "API key is not configured on the server."
}
```

Eksik ve geçersiz API anahtarı denemeleri yapılandırılmış loglara `WARNING` seviyesinde kaydedilir. Güvenlik nedeniyle gönderilen API anahtarının değeri loglanmaz.

## cURL ile API Kullanımı

Aşağıdaki örneklerde:

```text
your-secret-api-key
```

yerine `.env` dosyasında tanımladığınız API anahtarını kullanın.

### Sağlık kontrolü

Sağlık endpointi API anahtarı gerektirmez:

```bash
curl -X GET "http://127.0.0.1:8000/health"
```

### Tek event oluşturma

```bash
curl -X POST "http://127.0.0.1:8000/events/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key" \
  -d '{
    "category": "info",
    "platform": "Web",
    "os_version": "macOS 15",
    "device": "MacBook Air",
    "client_ts": 1753354000,
    "user_id": "user-1001",
    "session_id": "session-1001",
    "session_num": 1,
    "sdk_version": "1.0.0",
    "manufacturer": "Apple",
    "v": "1.0.0",
    "event_data": {
      "message": "Game started"
    }
  }'
```

### Batch event oluşturma

Tek istekte 1–100 event gönderilebilir:

```bash
curl -X POST "http://127.0.0.1:8000/events/batch" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key" \
  -d '{
    "events": [
      {
        "category": "info",
        "platform": "Web",
        "os_version": "macOS 15",
        "device": "MacBook Air",
        "client_ts": 1753354000,
        "user_id": "user-1001",
        "session_id": "batch-session-001",
        "session_num": 1,
        "sdk_version": "1.0.0",
        "manufacturer": "Apple",
        "v": "1.0.0",
        "event_data": {
          "message": "First batch event"
        }
      },
      {
        "category": "business",
        "platform": "Web",
        "os_version": "macOS 15",
        "device": "MacBook Air",
        "client_ts": 1753354100,
        "user_id": "user-1002",
        "session_id": "batch-session-002",
        "session_num": 1,
        "sdk_version": "1.0.0",
        "manufacturer": "Apple",
        "v": "1.0.0",
        "event_data": {
          "currency": "TRY",
          "amount": 250,
          "cart_type": "shop"
        }
      }
    ]
  }'
```

### Eventleri listeleme

```bash
curl -X GET "http://127.0.0.1:8000/events/?skip=0&limit=10" \
  -H "X-API-Key: your-secret-api-key"
```

### Kategori ve tarih aralığına göre filtreleme

```bash
curl -X GET "http://127.0.0.1:8000/events/?category=business&date_from=2026-08-01T00%3A00%3A00Z&date_to=2026-08-06T23%3A59%3A59Z&skip=0&limit=10" \
  -H "X-API-Key: your-secret-api-key"
```

### Kullanıcıya ait eventleri listeleme

```bash
curl -X GET "http://127.0.0.1:8000/events/user/user-1001?skip=0&limit=10" \
  -H "X-API-Key: your-secret-api-key"
```

### Günlük event sayılarını sorgulama

```bash
curl -X GET "http://127.0.0.1:8000/stats/daily-events" \
  -H "X-API-Key: your-secret-api-key"
```

### Aktif kullanıcı sayısını sorgulama

Bütün zamanlardaki benzersiz kullanıcıları saymak için:

```bash
curl -X GET "http://127.0.0.1:8000/stats/active-users" \
  -H "X-API-Key: your-secret-api-key"
```

Belirli bir tarih aralığı için:

```bash
curl -X GET "http://127.0.0.1:8000/stats/active-users?date_from=2026-08-01T00%3A00%3A00Z&date_to=2026-08-06T23%3A59%3A59Z" \
  -H "X-API-Key: your-secret-api-key"
```

## Veri Doğrulama

API aşağıdaki doğrulamaları uygular:

- Zorunlu alanların bulunması
- Alanların doğru veri tipine sahip olması
- Ana JSON seviyesindeki fazla alanların reddedilmesi
- `event_data` içindeki fazla alanların reddedilmesi
- `category` ile `event_data` modelinin eşleşmesi
- Temel metin alanlarının boş olmaması
- Yalnızca boşluklardan oluşan metinlerin reddedilmesi
- Metinlerin başındaki ve sonundaki gereksiz boşlukların temizlenmesi
- `session_num` ve miktar alanlarının sıfırdan büyük olması
- `client_ts` değerinin negatif olmaması
- Para biriminin üç büyük ve alfabetik harften oluşması
- `Literal` ile sınırlandırılmış değerlerin kontrolü
- `skip` ve `limit` parametrelerinin izin verilen aralıkta olması

Doğrulama hatalarında API:

```text
422 Unprocessable Entity
```

durum kodunu döndürür.

## Response Modelleri

API cevapları Pydantic response modelleriyle doğrulanmaktadır:

- `EventResponse`
- `EventCreateResponse`
- `EventListResponse`
- `UserEventListResponse`
- `BatchEventCreateResponse`
- `DailyEventStatsResponse`
- `ActiveUserStatsResponse`

Bu modeller:

- API cevaplarının standart bir yapıda kalmasını,
- Swagger dokümantasyonunda cevap alanlarının gösterilmesini,
- SQLAlchemy nesnelerinin güvenli şekilde JSON cevabına dönüştürülmesini,
- Batch işlemlerinde oluşturulan kayıt sayısının doğrulanmasını,
- İstatistik cevaplarının tanımlı bir yapıda döndürülmesini,
- Tanımlanmayan alanların istemciye gönderilmemesini

sağlar.

## Mevcut Durum

Tamamlanan temel özellikler:

- FastAPI tabanlı modüler proje yapısı
- Pydantic olay şemaları
- SQLite ve SQLAlchemy bağlantısı
- Tek event kaydetme
- Tek istekte 1–100 event kaydeden batch endpointi
- Genel event sorgulama
- Kullanıcıya göre event sorgulama
- `skip` ve `limit` ile sayfalama
- Event kategorisine göre filtreleme
- Başlangıç ve bitiş tarihine göre filtreleme
- Kategori ve `event_data` eşleşme kontrolü
- Katı alan doğrulaması
- Pydantic response modelleri
- Günlük event sayısı istatistikleri
- Benzersiz aktif kullanıcı istatistikleri
- Aktif kullanıcıların tarih aralığına göre filtrelenmesi
- Sağlık kontrolü dışındaki endpointlerde API key doğrulaması
- Eksik ve geçersiz API key denemelerinin güvenli şekilde loglanması
- Loguru ile yapılandırılmış loglama
- Terminal için okunabilir log çıktısı
- Dosya için JSON biçiminde log çıktısı
- Veritabanı hatalarında rollback işlemi
- `.env` üzerinden gizli yapılandırma yönetimi
- Veritabanı şema dokümanı
- Swagger ve cURL kullanım örnekleri
- pytest ile otomatik API testleri
- pytest-cov ile test kapsam raporu

## Testler ve Coverage

Projede API davranışlarını doğrulamak için `pytest` ve FastAPI `TestClient` kullanılmaktadır.

Her test için geçici ve bağımsız bir SQLite veritabanı oluşturulur. Böylece testler gerçek geliştirme veritabanını değiştirmez ve birbirlerinin verilerinden etkilenmez.

Test edilen başlıca senaryolar:

- Sağlık endpointi
- Başarılı tek event kaydı
- Eksik ve yanlış API key
- Event listeleme
- Kullanıcıya göre event listeleme
- Bilinmeyen kullanıcı için boş sonuç
- Pydantic alan ve veri tipi doğrulamaları
- Event kategorisi ile `event_data` eşleşmesi
- Genel ve kullanıcıya özel sayfalama
- Başarılı batch event kaydı
- Boş batch listesinin reddedilmesi
- Geçersiz event içeren batch isteğinde hiçbir kaydın oluşturulmaması
- Event kategorisine göre filtreleme
- Başarılı tarih aralığı filtrelemesi
- Ters tarih aralığının reddedilmesi
- Günlük event istatistikleri
- Benzersiz aktif kullanıcı sayısı
- Aktif kullanıcıların tarih aralığına göre filtrelenmesi

### Testleri çalıştırma

```bash
python -m pytest -v
```

Mevcut test sonucu:

```text
36 passed
```

### Coverage raporu

Eksik kalan satırları da gösteren coverage raporu:

```bash
python -m pytest --cov=app --cov-report=term-missing
```

Mevcut toplam test kapsamı:

```text
89%
```

Coverage dışında kalan satırların önemli bir bölümü, kasıtlı veritabanı hatası oluşturmayı gerektiren hata yönetimi ve rollback dallarıdır.

## Planlanan Geliştirmeler

- Alembic ile veritabanı migrasyonları
- Docker ve Docker Compose desteği
- PostgreSQL desteği
- GitHub Actions ile otomatik test ve coverage kontrolü
- DAF KDD'21 veri seti için import aracı
- Gelişmiş istatistik ve raporlama endpointleri
- Opsiyonel yük testi
- Üretim ortamına uygun deployment yapılandırması
