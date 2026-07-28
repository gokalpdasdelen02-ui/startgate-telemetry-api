# Startgate Telemetry API Servisi

Oyunlardan gelen telemetri olaylarını kabul eden, doğrulayan, veritabanında saklayan ve sorgulanabilir hâle getiren bir backend API servisidir.

API’ye gönderilen veriler Pydantic şemalarıyla doğrulanır. Geçerli olaylar SQLAlchemy ORM aracılığıyla SQLite veritabanına kaydedilir. Kaydedilen olaylar genel olarak veya kullanıcı kimliğine göre sayfalı şekilde sorgulanabilir.

## Özellikler

- Servis durumunu kontrol eden sağlık endpointi
- Tek bir telemetri olayını kabul eden ve kaydeden endpoint
- Pydantic ile veri tipi ve alan doğrulaması
- Olay kategorisi ile `event_data` içeriği arasında eşleşme kontrolü
- SQLAlchemy ORM ve SQLite ile kalıcı veri saklama
- Genel olay listeleme
- Kullanıcı kimliğine göre olay listeleme
- `skip` ve `limit` parametreleriyle sayfalama
- Sayfalama parametreleri için alt ve üst sınır kontrolü
- Pydantic response modelleriyle standart API cevapları
- Otomatik Swagger/OpenAPI dokümantasyonu
- UTC tabanlı olay zamanı oluşturma

## Kullanılan Teknolojiler

- **Dil:** Python 3.11+
- **Web çatısı:** FastAPI
- **ASGI sunucusu:** Uvicorn
- **Veri doğrulama:** Pydantic
- **ORM:** SQLAlchemy
- **Veritabanı:** SQLite
- **Kod biçimlendirme:** Black
- **Versiyon kontrolü:** Git ve GitHub

## Proje Mimarisi

```text
startgate-telemetry-api/
│
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI uygulamasının başlangıç noktası
│   ├── database.py         # Veritabanı bağlantısı ve session yönetimi
│   ├── models.py           # SQLAlchemy veritabanı modeli
│   ├── schemas.py          # Pydantic giriş ve cevap şemaları
│   ├── security.py         # API key doğrulaması
│   │
│   └── routers/
│       ├── __init__.py
│       └── events.py       # Olay kaydetme ve sorgulama endpointleri
│
├── docs/
│   └── veritabani-semasi.md
│
├── reports/
│   └── hafta-1.md
│
├── .env.example            # Ortam değişkenleri için örnek dosya
├── requirements.txt
├── telemetry.db
└── README.md
```

### Dosyaların Görevleri

- `main.py`: FastAPI uygulamasını oluşturur ve routerları uygulamaya bağlar.
- `database.py`: SQLAlchemy engine, session ve temel model sınıfını tanımlar.
- `models.py`: Veritabanındaki `game_events` tablosunu temsil eder.
- `schemas.py`: API’ye gelen verileri ve API’den dönen cevapları doğrular.
- `routers/events.py`: `/events` ile başlayan API endpointlerini içerir.

## Kurulum

### 1. Repoyu klonlayın

```bash
git clone https://github.com/gokalpdasdelen02-ui/startgate-telemetry-api.git
cd startgate-telemetry-api
```

### 2. Sanal ortam oluşturun

macOS veya Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Bağımlılıkları yükleyin

```bash
python -m pip install -r requirements.txt
```

macOS ortamında `python` komutu bulunamazsa:

```bash
python3 -m pip install -r requirements.txt
```

### 4. Ortam değişkenlerini yapılandırın

API’ye olay kaydetme işlemleri bir API anahtarıyla korunmaktadır.

Örnek ortam dosyasını kopyalayın:

macOS veya Linux:

```bash
cp .env.example .env
```

Windows:

```powershell
copy .env.example .env
```

Oluşan `.env` dosyasını açın ve kendi geliştirme anahtarınızı belirleyin:

```env
TELEMETRY_API_KEY=your-development-api-key
```

`.env` dosyası gizli bilgiler içerdiği için Git tarafından takip edilmez ve GitHub’a gönderilmez.

### 5. Uygulamayı çalıştırın

```bash
python -m uvicorn app.main:app --reload
```

Gerekirse macOS üzerinde:

```bash
python3 -m uvicorn app.main:app --reload
```

Sunucu varsayılan olarak şu adreste çalışır:

```text
http://127.0.0.1:8000
```

> Ana `/` endpointi tanımlı değildir. API’yi test etmek için `/docs` veya `/health` adreslerini kullanın.

## Swagger Dokümantasyonu

Uygulama çalışırken Swagger UI arayüzüne şu adresten ulaşabilirsiniz:

```text
http://127.0.0.1:8000/docs
```

Swagger üzerinden endpointler incelenebilir, örnek istekler gönderilebilir ve başarılı veya hatalı cevaplar görüntülenebilir.

`POST /events/` endpointini Swagger üzerinden test etmek için sayfanın üst kısmındaki **Authorize** düğmesine basın ve `.env` dosyanızda belirlediğiniz API anahtarını girin.

Anahtarın başına `Bearer` eklemeyin. Yalnızca anahtar değerini yazın.

## API Endpointleri

| Metot  | Endpoint                 | Açıklama                                                     |
| ------ | ------------------------ | ------------------------------------------------------------ |
| `GET`  | `/health`                | Servisin çalışıp çalışmadığını kontrol eder                  |
| `POST` | `/events/`               | Yeni bir telemetri olayı doğrular ve kaydeder                |
| `GET`  | `/events/`               | Bütün olayları sayfalı şekilde listeler                      |
| `GET`  | `/events/user/{user_id}` | Belirtilen kullanıcıya ait olayları sayfalı şekilde listeler |

## API Key Doğrulaması

Yeni bir olay oluşturmak için `POST /events/` isteğinde geçerli bir API anahtarı gönderilmelidir.

API anahtarı şu HTTP headerı içinde gönderilir:

```http
X-API-Key: your-development-api-key
```

API anahtarı JSON istek gövdesinin bir parçası değildir.

Endpointlerin erişim durumu:

| Endpoint                     | API key gerekli mi? |
| ---------------------------- | ------------------: |
| `GET /health`                |               Hayır |
| `POST /events/`              |                Evet |
| `GET /events/`               |               Hayır |
| `GET /events/user/{user_id}` |               Hayır |

Eksik veya geçersiz API anahtarında servis:

```text
401 Unauthorized
```

durum kodunu döndürür.

```json
{
  "detail": "Invalid or missing API key."
}
```

Sunucuda `TELEMETRY_API_KEY` ortam değişkeni yapılandırılmamışsa:

```text
500 Internal Server Error
```

durum kodu döndürülür.

## cURL ile API Kullanımı

Aşağıdaki örneklerde:

```text
your-development-api-key
```

ifadesini `.env` dosyanızda belirlediğiniz API anahtarıyla değiştirin.

### Sağlık kontrolü

```bash
curl -X GET "http://127.0.0.1:8000/health"
```

Beklenen cevap:

```json
{
  "status": "ok",
  "message": "Service is healthy."
}
```

### Yeni telemetri olayı oluşturma

```bash
curl -X POST "http://127.0.0.1:8000/events/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-development-api-key" \
  -d '{
    "category": "business",
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
      "currency": "TRY",
      "amount": 3500,
      "cart_type": "shop"
    }
  }'
```

Başarılı işlemde:

```text
201 Created
```

durum kodu döndürülür.

`timestamp` alanı gönderilmezse sunucu tarafından otomatik olarak UTC zamanıyla oluşturulur.

### Bütün olayları listeleme

```bash
curl -X GET "http://127.0.0.1:8000/events/?skip=0&limit=10"
```

Bu endpoint API anahtarı gerektirmez.

### Kullanıcıya ait olayları listeleme

```bash
curl -X GET \
  "http://127.0.0.1:8000/events/user/user-1001?skip=0&limit=10"
```

Belirtilen kullanıcıya ait kayıt bulunmazsa servis `200 OK` ve boş bir `data` listesi döndürür.

### API anahtarı olmadan POST denemesi

```bash
curl -X POST "http://127.0.0.1:8000/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "business",
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
      "currency": "TRY",
      "amount": 3500,
      "cart_type": "shop"
    }
  }'
```

Beklenen cevap:

```text
401 Unauthorized
```

```json
{
  "detail": "Invalid or missing API key."
}
```

## Sağlık Kontrolü

### İstek

```http
GET /health
```

### Örnek cevap

```json
{
  "status": "healthy"
}
```

## Yeni Olay Oluşturma

### İstek

```http
POST /events/
```

### Örnek business olayı

```json
{
  "category": "business",
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
    "currency": "TRY",
    "amount": 3500,
    "cart_type": "shop"
  }
}
```

`timestamp` alanı gönderilmezse sunucu tarafından otomatik olarak UTC biçiminde oluşturulur.

### Başarılı cevap

Başarılı bir kayıt işleminde API:

```text
201 Created
```

durum kodunu döndürür.

```json
{
  "status": "success",
  "message": "Event successfully saved to database.",
  "data": {
    "id": 1,
    "timestamp": "2026-07-24T12:10:56.258555",
    "category": "business",
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
      "currency": "TRY",
      "amount": 3500,
      "cart_type": "shop"
    }
  }
}
```

## Olayları Listeleme

### İstek

```http
GET /events/?skip=0&limit=10
```

### Sayfalama parametreleri

- `skip`: Başlangıçtan itibaren atlanacak kayıt sayısıdır. En az `0` olabilir.
- `limit`: Bir istekte döndürülecek en fazla kayıt sayısıdır. `1` ile `100` arasında olmalıdır.
- `total`: Veritabanındaki toplam kayıt sayısını gösterir.
- `count`: Mevcut sayfada dönen kayıt sayısını gösterir.

### Örnek cevap

```json
{
  "status": "success",
  "total": 25,
  "count": 10,
  "skip": 0,
  "limit": 10,
  "data": []
}
```

Olaylar en yeni kayıt önce gelecek şekilde sıralanır.

## Kullanıcıya Göre Olayları Listeleme

### İstek

```http
GET /events/user/user-1001?skip=0&limit=10
```

### Örnek cevap

```json
{
  "status": "success",
  "user_id": "user-1001",
  "total": 3,
  "count": 3,
  "skip": 0,
  "limit": 10,
  "data": []
}
```

Belirtilen kullanıcı kimliğine ait olay bulunmazsa istek yine başarılı kabul edilir ve boş liste döndürülür:

```json
{
  "status": "success",
  "user_id": "unknown-user",
  "total": 0,
  "count": 0,
  "skip": 0,
  "limit": 10,
  "data": []
}
```

## Desteklenen Olay Kategorileri

API şu olay kategorilerini desteklemektedir:

- `business`
- `progression`
- `design`
- `resource`
- `error`
- `user`
- `session_end`
- `ad`
- `impression`
- `info`

Her kategori, kendisine ait bir `event_data` yapısına sahiptir.

Örneğin `category` değeri `business` olduğunda `event_data`, `BusinessData` şemasına uygun olmalıdır. `business` kategorisi altında reklam verisi gönderilirse istek reddedilir.

## Veri Doğrulama

API aşağıdaki doğrulamaları uygular:

- Zorunlu alanların bulunması
- Alanların doğru veri tipine sahip olması
- Şemada bulunmayan fazla alanların reddedilmesi
- `session_num` ve miktar alanlarının sıfırdan büyük olması
- Para biriminin üç büyük harften oluşması
- `Literal` ile sınırlandırılmış değerlerin kontrolü
- `category` ve `event_data` modelinin birbiriyle eşleşmesi
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

Bu modeller:

- API cevaplarının standart bir yapıda kalmasını,
- Swagger dokümantasyonunda cevap alanlarının gösterilmesini,
- SQLAlchemy nesnelerinin güvenli şekilde JSON cevabına dönüştürülmesini,
- Tanımlanmayan alanların istemciye gönderilmemesini

sağlar.

## Mevcut Durum

Tamamlanan temel özellikler:

- FastAPI proje yapısı
- Pydantic olay şemaları
- SQLite ve SQLAlchemy bağlantısı
- Olay kaydetme
- Genel olay sorgulama
- Kullanıcıya göre olay sorgulama
- Sayfalama
- Kategori ve olay verisi eşleşme kontrolü
- Response modelleri
- Swagger üzerinden manuel testler

## Planlanan Geliştirmeler

- API key tabanlı kimlik doğrulama
- pytest ile otomatik API testleri
- Tarih ve olay kategorisine göre filtreleme
- Toplu olay kaydetme
- Yapılandırılmış loglama
- Özet istatistik endpointleri
- Alembic veritabanı migrasyonları
- Docker desteği
- PostgreSQL desteği
