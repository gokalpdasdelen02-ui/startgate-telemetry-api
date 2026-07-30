# API Tasarım Dokümanı — Startgate Telemetry API

Bu doküman, oyunlardan gelen telemetri olaylarını toplamak, doğrulamak, kalıcı olarak saklamak ve sorgulanabilir hâle getirmek amacıyla geliştirilen servisin uç noktalarını ve veri şemalarını tanımlar.

## 1. Uç Noktalar

Sistem aşağıdaki REST API uç noktalarını sağlamaktadır.

### GET `/health`

Servisin çalışır durumda olup olmadığını kontrol eder.

**Başarılı yanıt:**

```text
200 OK
```

```json
{
  "status": "ok",
  "message": "Service is healthy."
}
```

Bu endpoint API anahtarı gerektirmez.

---

### POST `/events/`

Oyun istemcisinden gelen yeni telemetri olayını kabul eder, Pydantic şemalarıyla doğrular ve SQLAlchemy ORM aracılığıyla SQLite veritabanına kaydeder.

**Kimlik doğrulaması:**

Bu endpoint geçerli bir API anahtarı gerektirir. Anahtar aşağıdaki HTTP headerı ile gönderilir:

```http
X-API-Key: your-development-api-key
```

API anahtarı JSON gövdesinin bir parçası değildir.

**İstek gövdesi:**

`GameEvent` JSON yapısı kullanılır.

**Örnek istek gövdesi:**

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

`timestamp` alanı gönderilmezse sunucu tarafından otomatik olarak UTC zamanıyla oluşturulur.

**Başarılı yanıt:**

```text
201 Created
```

```json
{
  "status": "success",
  "message": "Event successfully saved to database.",
  "data": {
    "id": 1,
    "timestamp": "2026-07-28T10:30:00.000000",
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

**Olası hata durumları:**

- Eksik veya geçersiz API anahtarı: `401 Unauthorized`
- Geçersiz istek verisi: `422 Unprocessable Entity`
- Sunucuda API anahtarı yapılandırılmamışsa: `500 Internal Server Error`
- Veritabanı kayıt işlemi başarısız olursa: `500 Internal Server Error`

Eksik veya geçersiz API anahtarında aşağıdaki cevap döndürülür:

```json
{
  "detail": "Invalid or missing API key."
}
```

Sunucuda API anahtarı yapılandırılmamışsa aşağıdaki cevap döndürülür:

```json
{
  "detail": "API key is not configured on the server."
}
```

Veritabanı kayıt işlemi başarısız olursa aşağıdaki cevap döndürülür:

```json
{
  "detail": "Event could not be saved to the database."
}
```

Veritabanı işlemi sırasında SQLAlchemy kaynaklı bir hata oluşursa başarısız transaction `rollback()` ile geri alınır.

---

### GET `/events/`

Veritabanına kaydedilmiş bütün telemetri olaylarını sayfalı biçimde listeler.

**Query parametreleri:**

- `skip`: Atlanacak kayıt sayısıdır. Varsayılan değeri `0`, en küçük değeri `0`dır.
- `limit`: Döndürülecek en fazla kayıt sayısıdır. Varsayılan değeri `10`, izin verilen aralık `1–100`dür.

**Örnek istek:**

```http
GET /events/?skip=0&limit=10
```

**Başarılı yanıt:**

```text
200 OK
```

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

- `total`: Veritabanındaki toplam olay sayısını gösterir.
- `count`: Mevcut sayfada döndürülen kayıt sayısını gösterir.
- `skip`: Atlanan kayıt sayısını gösterir.
- `limit`: Bir sayfada istenen en fazla kayıt sayısını gösterir.
- `data`: Döndürülen telemetri olaylarının listesidir.

Olaylar en yeni kayıt önce gelecek şekilde sıralanır.

Bu endpoint API anahtarı gerektirmez.

---

### GET `/events/user/{user_id}`

Belirtilen kullanıcı kimliğine ait telemetri olaylarını sayfalı biçimde listeler.

**Path parametresi:**

- `user_id`: Olayları sorgulanacak kullanıcının kimliğidir.

**Query parametreleri:**

- `skip`: Atlanacak kayıt sayısıdır. Varsayılan değeri `0`dır.
- `limit`: Döndürülecek en fazla kayıt sayısıdır. Varsayılan değeri `10`, izin verilen aralık `1–100`dür.

**Örnek istek:**

```http
GET /events/user/user-1001?skip=0&limit=10
```

**Başarılı yanıt:**

```text
200 OK
```

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

Belirtilen kullanıcıya ait olay bulunmazsa endpoint yine `200 OK` döndürür:

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

Ayrı bir kullanıcı tablosu bulunmadığı için sistem, kullanıcının mevcut olup olmadığını değil, yalnızca o `user_id` değerine ait telemetri kaydı bulunup bulunmadığını kontrol eder.

Bu endpoint API anahtarı gerektirmez.

---

## 2. Olay Şeması

API’ye gönderilen telemetri verileri Pydantic şemalarıyla doğrulanmaktadır.

Ana istek modeli `GameEvent` sınıfıdır.

### Ortak Alanlar

Her telemetri olayında aşağıdaki ortak alanlar bulunur:

- `timestamp`: Etkinlik zamanı. Opsiyoneldir; gönderilmezse sunucu tarafından UTC olarak oluşturulur.
- `category`: Olay kategorisidir.
- `platform`: Kullanıcı platformudur. Örneğin `iOS`, `Android` veya `Web`.
- `os_version`: İşletim sistemi sürümüdür.
- `device`: Cihaz modelidir.
- `manufacturer`: Cihaz üreticisidir.
- `client_ts`: İstemci tarafındaki Unix zaman damgasıdır. Negatif olamaz.
- `user_id`: Kullanıcının benzersiz kimliğidir.
- `session_id`: Olayın ait olduğu oturumun kimliğidir.
- `session_num`: Kullanıcının oturum numarasıdır. Sıfırdan büyük olmalıdır.
- `sdk_version`: Kullanılan telemetri SDK sürümüdür.
- `v`: Oyun veya uygulama sürümüdür.
- `event_data`: Kategoriye özel verileri içeren nesnedir.

Desteklenen kategoriler:

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

---

## 3. Dinamik Alt Şemalar

`event_data` içeriği, `category` alanına göre farklı bir Pydantic modeliyle doğrulanır.

Kategori ile `event_data` modeli birbiriyle uyumlu olmak zorundadır.

Kategori-model eşleşmeleri:

| Kategori      | Beklenen model    |
| ------------- | ----------------- |
| `business`    | `BusinessData`    |
| `progression` | `ProgressionData` |
| `design`      | `DesignData`      |
| `resource`    | `ResourceData`    |
| `error`       | `ErrorData`       |
| `user`        | `UserData`        |
| `session_end` | `SessionEndData`  |
| `ad`          | `AdData`          |
| `impression`  | `ImpressionData`  |
| `info`        | `InfoData`        |

Örneğin `category` değeri `business` olduğunda `event_data`, `BusinessData` modeline uygun olmalıdır.

`business` kategorisi altında reklam verisi gönderilirse istek reddedilir.

### BusinessData

Gerçek para işlemlerini takip eder.

Alanlar:

- `currency`: Üç büyük harften oluşan para birimi kodudur. Örneğin `USD` veya `TRY`.
- `amount`: Sıfırdan büyük işlem miktarıdır.
- `cart_type`: Satın alma işleminin gerçekleştiği yerdir. Opsiyoneldir.

Örnek:

```json
{
  "currency": "TRY",
  "amount": 3500,
  "cart_type": "shop"
}
```

### ProgressionData

Oyuncunun bölüm veya görev ilerlemesini takip eder.

Alanlar:

- `status`: `Start`, `Complete` veya `Fail`
- `progression_01`: Ana bölüm veya görev adı
- `progression_02`: Opsiyonel alt bölüm bilgisi
- `progression_03`: Opsiyonel ek bölüm bilgisi
- `score`: Opsiyonel skor

Örnek:

```json
{
  "status": "Complete",
  "progression_01": "level_01",
  "progression_02": "phase_1",
  "score": 1500
}
```

### DesignData

Oyuncunun oyun içindeki özel davranışlarını veya tasarım olaylarını takip eder.

Alanlar:

- `event_id`: Tasarım olayının adıdır.
- `value`: Olayla ilişkili opsiyonel sayısal değerdir.

Örnek:

```json
{
  "event_id": "ui:click:play",
  "value": 1
}
```

### ResourceData

Oyun içi sanal kaynakların kazanılmasını veya harcanmasını takip eder.

Alanlar:

- `flow_type`: `Sink` veya `Source`
- `currency`: Kaynak türü
- `item_type`: Öğenin kategorisi
- `item_id`: Öğenin kimliği
- `amount`: Sıfırdan büyük miktar

Örnek:

```json
{
  "flow_type": "Source",
  "currency": "Gold",
  "item_type": "Reward",
  "item_id": "Daily_Reward",
  "amount": 100
}
```

### ErrorData

Oyun veya istemci tarafında oluşan hataları kaydeder.

Alanlar:

- `severity`: `debug`, `info`, `warning`, `error` veya `critical`
- `message`: Hata mesajı veya stack trace

Örnek:

```json
{
  "severity": "error",
  "message": "Connection timeout"
}
```

### UserData

Kullanıcıya ait opsiyonel özel verileri saklar.

Alanlar:

- `custom_01`: Opsiyonel kullanıcı verisi

Örnek:

```json
{
  "custom_01": "premium-user"
}
```

### SessionEndData

Bir oyun oturumunun sona ermesini takip eder.

Alanlar:

- `length`: Oturumun saniye cinsinden uzunluğudur ve sıfırdan büyük olmalıdır.

Örnek:

```json
{
  "length": 900
}
```

### AdData

Reklam etkileşimlerini takip eder.

Alanlar:

- `ad_action`: Reklamla gerçekleştirilen etkileşim
- `ad_type`: Reklam formatı
- `ad_sdk_name`: Reklam ağı veya SDK adı
- `ad_placement`: Reklamın gösterildiği konum

İzin verilen `ad_action` değerleri:

- `clicked`
- `show`
- `failed`
- `reward_received`
- `request`

İzin verilen `ad_type` değerleri:

- `video`
- `rewarded_video`
- `playable`
- `interstitial`
- `banner`

Örnek:

```json
{
  "ad_action": "show",
  "ad_type": "rewarded_video",
  "ad_sdk_name": "admob",
  "ad_placement": "end_of_level"
}
```

### ImpressionData

Reklam gösterim bilgilerini takip eder.

Alanlar:

- `ad_network_name`: Reklam ağının adı
- `ad_network_version`: Reklam ağının SDK sürümü

Örnek:

```json
{
  "ad_network_name": "ironSource",
  "ad_network_version": "8.0.0"
}
```

### InfoData

Genel bilgi veya log mesajlarını kaydeder.

Alanlar:

- `message`: Kaydedilecek bilgi mesajı

Örnek:

```json
{
  "message": "Player opened the settings screen."
}
```

---

## 4. Veri Doğrulama Kuralları

API aşağıdaki doğrulamaları uygular:

- Zorunlu alanların bulunması
- Alanların doğru veri tipinde olması
- Ana JSON seviyesindeki tanımsız alanların reddedilmesi
- `event_data` içindeki tanımsız alanların reddedilmesi
- Kategori ile `event_data` modelinin eşleşmesi
- Temel metin alanlarının boş olmaması
- Yalnızca boşluklardan oluşan temel metinlerin reddedilmesi
- Temel metinlerin başındaki ve sonundaki gereksiz boşlukların temizlenmesi
- `session_num` değerinin sıfırdan büyük olması
- `client_ts` değerinin negatif olmaması
- Miktar alanlarının sıfırdan büyük olması
- Para biriminin üç büyük harften oluşması
- Para biriminin yalnızca alfabetik karakterlerden oluşması
- Para biriminin büyük harflerle yazılması
- `Literal` ile tanımlanmış alanlarda yalnızca izin verilen değerlerin kabul edilmesi
- Sayfalama parametrelerinde `skip` değerinin negatif olmaması
- Sayfalama parametrelerinde `limit` değerinin `1–100` arasında olması

Geçersiz isteklerde API:

```text
422 Unprocessable Entity
```

durum kodunu döndürür.

---

## 5. API Key Doğrulaması

Yeni olay oluşturma işlemi API anahtarıyla korunmaktadır.

API anahtarı istemci tarafından aşağıdaki HTTP headerı ile gönderilir:

```http
X-API-Key: your-development-api-key
```

Sunucudaki beklenen API anahtarı `.env` dosyasındaki şu ortam değişkeninden okunur:

```env
TELEMETRY_API_KEY=your-development-api-key
```

Gerçek `.env` dosyası gizli bilgiler içerdiği için Git tarafından takip edilmez.

Repoda yalnızca örnek yapı içeren `.env.example` dosyası bulunur.

Endpointlerin erişim durumu:

| Endpoint                     | API key gerekli mi? |
| ---------------------------- | ------------------: |
| `GET /health`                |               Hayır |
| `POST /events/`              |                Evet |
| `GET /events/`               |                Evet |
| `GET /events/user/{user_id}` |                Evet |

API anahtarı karşılaştırması `secrets.compare_digest()` kullanılarak gerçekleştirilir.

---

## 6. Veritabanı Yapısı

Telemetri olayları yerel SQLite veritabanındaki `game_events` tablosunda saklanır.

SQLAlchemy ORM, Python nesneleri ile veritabanı tablosu arasındaki eşlemeyi yönetir.

Kategoriye göre değişen `event_data` içeriği JSON kolonunda saklanır. Ortak olay alanları ise ayrı veritabanı kolonlarında tutulur.

Veritabanında kullanılan temel alanlar:

- `id`
- `user_id`
- `category`
- `event_data`
- `timestamp`
- `session_id`
- `platform`
- `session_num`
- `os_version`
- `sdk_version`
- `device`
- `manufacturer`
- `v`
- `client_ts`

`id` alanı tablonun primary key alanıdır.

`user_id`, `category`, `session_id` ve `platform` alanlarında sorgu performansını desteklemek amacıyla index bulunmaktadır.

Zorunlu veritabanı kolonlarında `nullable=False` kullanılmaktadır.

Veritabanı kolonları ve tasarım kararları için [veritabanı şema dokümanını](docs/veritabani-semasi.md) inceleyebilirsiniz.

---

## 7. Veritabanı Hata Yönetimi

Yeni olay oluşturulurken aşağıdaki veritabanı işlemleri gerçekleştirilir:

```text
db.add()
db.commit()
db.refresh()
```

Veritabanı işlemi sırasında SQLAlchemy kaynaklı hata oluşursa:

1. Hata `SQLAlchemyError` ile yakalanır.
2. Başarısız transaction `db.rollback()` ile geri alınır.
3. İstemciye kontrollü bir `500 Internal Server Error` cevabı gönderilir.

Bu yapı, başarısız bir transaction sonrasında SQLAlchemy sessionının hatalı durumda kalmasını engeller.

Teknik veritabanı hata ayrıntıları doğrudan istemciye gönderilmez.

---

## 8. Response Modelleri

API cevapları aşağıdaki Pydantic response modelleriyle doğrulanır:

- `EventResponse`
- `EventCreateResponse`
- `EventListResponse`
- `UserEventListResponse`

### EventResponse

Tek bir telemetri olayının cevap yapısını tanımlar.

SQLAlchemy nesnelerindeki alanların okunabilmesi için:

```python
ConfigDict(from_attributes=True)
```

yapılandırması kullanılır.

### EventCreateResponse

Yeni olay oluşturma işleminin başarılı cevap yapısını tanımlar.

Alanlar:

- `status`
- `message`
- `data`

### EventListResponse

Genel olay listeleme endpointinin cevap yapısını tanımlar.

Alanlar:

- `status`
- `total`
- `count`
- `skip`
- `limit`
- `data`

### UserEventListResponse

Kullanıcıya göre olay listeleme endpointinin cevap yapısını tanımlar.

Alanlar:

- `status`
- `user_id`
- `total`
- `count`
- `skip`
- `limit`
- `data`

Response modelleri:

- API cevaplarının standart yapıda kalmasını,
- Swagger dokümantasyonunda cevap alanlarının görüntülenmesini,
- SQLAlchemy nesnelerinin JSON cevabına dönüştürülmesini,
- Tanımlanmayan alanların istemciye gönderilmemesini

sağlar.

---

## 9. Kullanılan Teknolojiler

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy ORM
- SQLite
- python-dotenv
- Swagger / OpenAPI
- Black Formatter
- Git ve GitHub

---

## 10. Genel Veri Akışı

Yeni bir olay oluşturma isteğinin sistem içindeki akışı şöyledir:

```text
İstemci POST isteği
        ↓
X-API-Key doğrulaması
        ↓
Pydantic GameEvent doğrulaması
        ↓
Kategori ve event_data eşleşme kontrolü
        ↓
SQLAlchemy GameEvent nesnesi
        ↓
SQLite veritabanına kayıt
        ↓
Response model doğrulaması
        ↓
201 Created cevabı
```

Doğrulama veya kayıt sırasında hata oluşursa akış ilgili aşamada durdurulur ve uygun HTTP durum kodu döndürülür.
