# API Tasarım Dokümanı — Startgate Telemetry API

Bu doküman, oyunlardan gelen telemetri olaylarını toplamak, doğrulamak, kalıcı olarak saklamak ve sorgulanabilir hâle getirmek amacıyla geliştirilen servisin uç noktalarını ve veri şemalarını tanımlar.

## 1. Uç Noktalar

Sistem aşağıdaki REST API uç noktalarını sağlamaktadır.

Sağlık kontrolü dışındaki bütün event ve istatistik endpointleri `X-API-Key` headerı ile korunmaktadır.

| Metot  | Endpoint                 | Açıklama                                       | API key  |
| ------ | ------------------------ | ---------------------------------------------- | -------- |
| `GET`  | `/health`                | Servisin sağlık durumunu kontrol eder          | Gerekmez |
| `POST` | `/events/`               | Tek bir telemetri eventini kaydeder            | Gerekli  |
| `POST` | `/events/batch`          | Tek istekte birden fazla eventi kaydeder       | Gerekli  |
| `GET`  | `/events/`               | Eventleri filtreleme ve sayfalama ile listeler | Gerekli  |
| `GET`  | `/events/user/{user_id}` | Belirli kullanıcıya ait eventleri listeler     | Gerekli  |
| `GET`  | `/stats/daily-events`    | Event sayılarını günlere göre gruplar          | Gerekli  |
| `GET`  | `/stats/active-users`    | Benzersiz aktif kullanıcı sayısını döndürür    | Gerekli  |

---

### GET `/health`

Servisin çalışır durumda olup olmadığını kontrol eder.

Bu endpoint API anahtarı gerektirmez.

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

---

### POST `/events/`

Oyun istemcisinden gelen tek bir telemetri eventini kabul eder, Pydantic ile doğrular ve SQLAlchemy aracılığıyla veritabanına kaydeder.

**Kimlik doğrulaması:**

```http
X-API-Key: your-secret-api-key
```

API anahtarı JSON gövdesinin bir parçası değildir.

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

`timestamp` alanı gönderilmezse sunucu tarafından UTC zamanı kullanılarak otomatik oluşturulur.

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
    "timestamp": "2026-08-07T08:30:00Z",
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

| Durum                                   | HTTP kodu                   |
| --------------------------------------- | --------------------------- |
| Eksik veya geçersiz API anahtarı        | `401 Unauthorized`          |
| Geçersiz istek verisi                   | `422`                       |
| Sunucuda API anahtarı yapılandırılmamış | `500 Internal Server Error` |
| Veritabanına kayıt başarısız            | `500 Internal Server Error` |

Veritabanı işlemi sırasında SQLAlchemy kaynaklı hata oluşursa transaction `rollback()` ile geri alınır.

---

### POST `/events/batch`

Tek HTTP isteğinde birden fazla telemetri eventinin kaydedilmesini sağlar.

Bir batch isteği en az `1`, en fazla `100` event içerebilir.

**Örnek istek:**

```json
{
  "events": [
    {
      "category": "info",
      "platform": "Web",
      "os_version": "macOS 15",
      "device": "MacBook Air",
      "client_ts": 1754388000,
      "user_id": "batch-user-001",
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
      "client_ts": 1754388001,
      "user_id": "batch-user-002",
      "session_id": "batch-session-002",
      "session_num": 1,
      "sdk_version": "1.0.0",
      "manufacturer": "Apple",
      "v": "1.0.0",
      "event_data": {
        "currency": "TRY",
        "amount": 2500,
        "cart_type": "shop"
      }
    }
  ]
}
```

**Başarılı yanıt:**

```text
201 Created
```

```json
{
  "status": "success",
  "message": "Events successfully saved to database.",
  "created_count": 2,
  "data": []
}
```

Batch içerisindeki eventlerden biri Pydantic doğrulamasından geçemezse istek `422` ile reddedilir ve endpoint çalıştırılmadığı için hiçbir event kaydedilmez.

Veritabanı işlemleri tek transaction içerisinde gerçekleştirilir ve SQLAlchemy hatasında `rollback()` uygulanır.

---

### GET `/events/`

Veritabanına kaydedilmiş telemetri eventlerini filtreleme ve sayfalama desteğiyle listeler.

**Query parametreleri:**

| Parametre   | Tip      | Zorunlu | Açıklama                                                   |
| ----------- | -------- | ------- | ---------------------------------------------------------- |
| `category`  | string   | Hayır   | Event kategorisine göre filtreler                          |
| `date_from` | datetime | Hayır   | Bu tarih ve sonrasındaki eventleri getirir                 |
| `date_to`   | datetime | Hayır   | Bu tarih ve öncesindeki eventleri getirir                  |
| `skip`      | integer  | Hayır   | Atlanacak kayıt sayısı, varsayılan `0`                     |
| `limit`     | integer  | Hayır   | Döndürülecek kayıt sayısı, varsayılan `10`, maksimum `100` |

**Örnek istek:**

```http
GET /events/?category=business&date_from=2026-08-01T00:00:00Z&date_to=2026-08-06T23:59:59Z&skip=0&limit=10
```

**Başarılı yanıt:**

```text
200 OK
```

```json
{
  "status": "success",
  "total": 3,
  "count": 3,
  "skip": 0,
  "limit": 10,
  "data": []
}
```

`total`, uygulanan filtrelere uyan toplam event sayısını gösterir. `count` ise mevcut sayfada döndürülen event sayısıdır.

Eventler en yeni kayıt önce gelecek şekilde sıralanır.

`date_from`, `date_to` değerinden sonra ise API `422` döndürür.

---

### GET `/events/user/{user_id}`

Belirtilen kullanıcı kimliğine ait telemetri eventlerini sayfalı biçimde listeler.

**Parametreler:**

| Parametre | Tür   | Açıklama                                                   |
| --------- | ----- | ---------------------------------------------------------- |
| `user_id` | path  | Eventleri sorgulanacak kullanıcı kimliği                   |
| `skip`    | query | Atlanacak kayıt sayısı, varsayılan `0`                     |
| `limit`   | query | Döndürülecek kayıt sayısı, varsayılan `10`, maksimum `100` |

**Örnek istek:**

```http
GET /events/user/user-1001?skip=0&limit=10
```

**Başarılı yanıt:**

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

Belirtilen `user_id` değerine ait event bulunmazsa endpoint hata üretmek yerine `200 OK` ve boş `data` listesi döndürür.

Sistemde ayrı bir kullanıcı tablosu bulunmadığı için endpoint kullanıcının varlığını değil, o `user_id` değerine ait telemetri kayıtlarını sorgular.

---

### GET `/stats/daily-events`

Veritabanındaki eventleri tarihlerine göre gruplar ve her gün için toplam event sayısını döndürür.

**Örnek istek:**

```http
GET /stats/daily-events
```

**Başarılı yanıt:**

```json
{
  "status": "success",
  "data": [
    {
      "date": "2026-08-05",
      "event_count": 4
    },
    {
      "date": "2026-08-06",
      "event_count": 7
    }
  ]
}
```

Sonuçlar tarihe göre artan sırada döndürülür.

---

### GET `/stats/active-users`

En az bir telemetri eventi göndermiş benzersiz kullanıcıların sayısını döndürür.

Aynı kullanıcının birden fazla eventi olsa bile kullanıcı yalnızca bir kez sayılır.

**Query parametreleri:**

| Parametre   | Tip      | Zorunlu | Açıklama                                                       |
| ----------- | -------- | ------- | -------------------------------------------------------------- |
| `date_from` | datetime | Hayır   | Bu tarih ve sonrasında event gönderen kullanıcıları dahil eder |
| `date_to`   | datetime | Hayır   | Bu tarih ve öncesinde event gönderen kullanıcıları dahil eder  |

Parametre verilmezse tüm event kayıtları üzerinden benzersiz kullanıcı sayısı hesaplanır.

**Örnek istek:**

```http
GET /stats/active-users?date_from=2026-08-01T00:00:00Z&date_to=2026-08-06T23:59:59Z
```

**Başarılı yanıt:**

```json
{
  "status": "success",
  "active_users": 5
}
```

Eşleşen kullanıcı yoksa:

```json
{
  "status": "success",
  "active_users": 0
}
```

`date_from`, `date_to` değerinden sonra ise API `422` döndürür.

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

API, gelen telemetri verilerinin beklenen yapıya uygun ve güvenli olmasını sağlamak için Pydantic tabanlı katı doğrulama uygular.

Uygulanan temel doğrulamalar:

- Zorunlu alanların bulunması
- Alanların doğru veri tipinde olması
- Ana JSON seviyesindeki tanımsız alanların reddedilmesi
- `event_data` içindeki tanımsız alanların reddedilmesi
- `category` ile `event_data` modelinin eşleşmesi
- Temel metin alanlarının boş olmaması
- Yalnızca boşluklardan oluşan temel metinlerin reddedilmesi
- Temel metinlerin başındaki ve sonundaki gereksiz boşlukların temizlenmesi
- `session_num` değerinin sıfırdan büyük olması
- `client_ts` değerinin negatif olmaması
- Miktar alanlarının sıfırdan büyük olması
- Para biriminin tam olarak üç alfabetik karakterden oluşması
- Para biriminin büyük harflerle yazılması
- `Literal` ile tanımlanan alanlarda yalnızca izin verilen değerlerin kabul edilmesi
- Batch isteğinin en az `1`, en fazla `100` event içermesi
- `skip` değerinin negatif olmaması
- `limit` değerinin `1–100` arasında olması
- `date_from` ve `date_to` parametrelerinin geçerli datetime değerleri olması
- `date_from` değerinin `date_to` değerinden sonra olmaması

### Kategori ve `event_data` Eşleşmesi

Her event kategorisi yalnızca kendisine ait `event_data` modeliyle kullanılabilir.

Örneğin:

```text
category = business
```

## 5. API Key Doğrulaması

API, telemetri verilerine yetkisiz erişimi engellemek için `X-API-Key` tabanlı temel kimlik doğrulama kullanır.

Sağlık kontrolü dışındaki bütün event ve istatistik endpointleri API anahtarı gerektirir.

| Metot  | Endpoint                                   | API Key  |
| ------ | ------------------------------------------ | -------- |
| `GET`  | `/health`                                  | Gerekmez |
| `POST` | `/events/`                                 | Gerekli  |
| `POST` | `/events/batch`                            | Gerekli  |
| `GET`  | `/events/`                                 | Gerekli  |
| `GET`  | `/events/user/{ kimlik doğrulama kullanır. |

Sağlık kontrolü dışındaki bütün event ve istatistik endpointleri API anahtarı gerektirir.

| Metot  | Endpoint              | API Key        |
| ------ | --------------------- | -------------- | ------- |
| `GET`  | `/health`             | Gerekmez       |
| `POST` | `/events/`            | Gerekuser_id}` | Gerekli |
| `GET`  | `/stats/daily-events` | Gerekli        |
| `GET`  | `/stats/active-users` | Gerekli        |

### API Anahtarının Gönderilmesi

API anahtarı HTTP isteğinin header bölümünde gönderilir:

```http
X-API-Key: your-secret-api-key
```

API anahtarı JSON request body içerisinde gönderilmez.

Anahtar `.env` dosyasında aşağıdaki ortam değişkeni ile tanımlanır:

```env
TELEMETRY_API_KEY=your-secret-api-key
```

Gerçek `.env` dosyası Git reposuna eklenmez. Gerekli yapılandırmanın gösterilmesi için `.env.example` kullanılır.

### Anahtarın Doğrulanması

İstemciden gelen API anahtarı ile sunucuda yapılandırılan anahtar güvenli biçimde karşılaştırılır.

Karşılaştırma sırasında:

```python
secrets.compare_digest()
```

kullanılır.

Bu yöntem iki değerin karşılaştırılması sırasında oluşabilecek zamanlama farklılıklarını azaltmak amacıyla tercih edilmiştir.

### Eksik veya Geçersiz API Anahtarı

API anahtarı gönderilmezse veya gönderilen anahtar geçerli değilse:

```text
401 Unauthorized
```

durum kodu döndürülür.

Örnek cevap:

```json
{
  "detail": "Invalid or missing API key."
}
```

### Sunucuda API Anahtarı Yapılandırılmamışsa

Sunucuda `TELEMETRY_API_KEY` ortam değişkeni tanımlanmamışsa bu durum istemci hatası değil, sunucu yapılandırma hatası olarak değerlendirilir.

API:

```text
500 Internal Server Error
```

durum kodu döndürür.

Örnek cevap:

```json
{
  "detail": "API key is not configured on the server."
}
```

### Swagger Üzerinden Kullanım

Swagger arayüzünde korunan endpointleri kullanmak için `Authorize` butonundan API anahtarı girilebilir.

Buraya yalnızca anahtar değeri yazılır:

```text
your-secret-api-key
```

`Bearer` öneki kullanılmaz.

Yetkilendirme yapıldıktan sonra Swagger, korunan endpointlere gönderilen isteklerde `X-API-Key` headerını otomatik olarak ekler.

### Güvenlik Logları

Eksik veya geçersiz API key denemeleri yapılandırılmış loglara `WARNING` seviyesinde kaydedilir.

Sunucuda API anahtarı yapılandırılmamışsa durum `ERROR` seviyesinde loglanır.

Güvenlik nedeniyle gerçek API anahtarı hiçbir zaman loglara yazılmaz.

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

Veritabanı işlemleri SQLAlchemy üzerinden gerçekleştirilir ve olası veritabanı hataları kontrollü şekilde ele alınır.

Veritabanı erişimi sırasında oluşabilecek `SQLAlchemyError` hataları endpoint seviyesinde yakalanır.

### Event Oluşturma

`POST /events/` endpointinde event veritabanına eklenir ve transaction tamamlanır.

Veritabanı işlemi sırasında hata oluşursa:

```python
db.rollback()
```

çalıştırılarak transaction geri alınır.

İstemciye:

```text
500 Internal Server Error
```

durum kodu döndürülür.

Böylece başarısız bir veritabanı işleminin session üzerinde açık veya hatalı bir transaction bırakması engellenir.

### Batch Event Oluşturma

`POST /events/batch` endpointinde birden fazla event aynı veritabanı işlemi kapsamında kaydedilir.

Batch içerisindeki eventler önce Pydantic tarafından doğrulanır. Herhangi bir event doğrulamadan geçemezse endpoint çalıştırılmaz ve veritabanına hiçbir kayıt gönderilmez.

Veritabanı işlemi sırasında SQLAlchemy hatası oluşursa:

```python
db.rollback()
```

uygulanır ve istemciye:

```text
500 Internal Server Error
```

cevabı döndürülür.

### Event Sorguları

Aşağıdaki endpointlerde meydana gelen SQLAlchemy sorgu hataları da kontrollü şekilde ele alınır:

```text
GET /events/
GET /events/user/{user_id}
```

Sorgu sırasında veritabanı hatası oluşursa transaction temizlenir ve istemciye `500 Internal Server Error` cevabı döndürülür.

### İstatistik Sorguları

İstatistik endpointlerinde de aynı hata yönetimi yaklaşımı uygulanır:

```text
GET /stats/daily-events
GET /stats/active-users
```

Günlük event sayıları veya aktif kullanıcı istatistikleri sorgulanırken SQLAlchemy kaynaklı hata oluşursa işlem yakalanır, session geri alınır ve istemciye sunucu hatası döndürülür.

### Yapılandırılmış Hata Logları

Veritabanı hataları Loguru ile yapılandırılmış biçimde loglanır.

Hata kayıtlarında:

- Gerçekleşen işlem
- İlgili filtre veya event bilgileri
- Hata seviyesi
- Exception ve traceback bilgileri

kaydedilebilir.

Veritabanı hataları:

```text
database_error
```

olay adıyla `ERROR` seviyesinde kaydedilir.

`logger.exception()` kullanıldığı durumlarda exception traceback bilgisi de loglara eklenir.

### Doğrulama Hataları ile Veritabanı Hatalarının Ayrımı

Pydantic doğrulamasından geçemeyen istekler veritabanı işlemine ulaşmadan reddedilir.

Bu tür hatalar:

```text
422 Unprocessable Content
```

olarak döner.

Veritabanı işlemi başladıktan sonra oluşan SQLAlchemy kaynaklı hatalar ise:

```text
500 Internal Server Error
```

olarak değerlendirilir.

Bu ayrım sayesinde istemci kaynaklı hatalar ile sunucu/veritabanı kaynaklı hatalar birbirinden ayrılır.

## 8. Response Modelleri

API cevaplarının belirli ve tutarlı bir yapıda kalması için Pydantic response modelleri kullanılmaktadır.

Kullanılan response modelleri:

- `EventResponse`
- `EventCreateResponse`
- `BatchEventCreateResponse`
- `EventListResponse`
- `UserEventListResponse`
- `DailyEventCount`
- `DailyEventStatsResponse`
- `ActiveUserStatsResponse`

### EventResponse

Tek bir telemetri eventinin API cevabındaki yapısını tanımlar.

`GameEvent` modelindeki bütün event alanlarına ek olarak veritabanı tarafından oluşturulan:

```text
id
```

## 9. Kullanılan Teknolojiler

Projede aşağıdaki teknolojiler ve araçlar kullanılmaktadır:

| Teknoloji / Araç       | Kullanım Amacı                                          |
| ---------------------- | ------------------------------------------------------- |
| **Python**             | Uygulamanın ana programlama dili                        |
| **FastAPI**            | REST API geliştirme                                     |
| **Pydantic**           | Request ve response modelleri, veri doğrulama           |
| **SQLAlchemy**         | ORM ve veritabanı işlemleri                             |
| **SQLite**             | Geliştirme ve mevcut uygulama veritabanı                |
| **Uvicorn**            | ASGI sunucusu                                           |
| **Loguru**             | Yapılandırılmış uygulama logları                        |
| **pytest**             | Otomatik testlerin çalıştırılması                       |
| **HTTPX / TestClient** | API endpointlerinin test edilmesi                       |
| **pytest-cov**         | Test kapsamının ölçülmesi                               |
| **python-dotenv**      | `.env` ortam değişkenlerinin yüklenmesi                 |
| **Swagger / OpenAPI**  | Otomatik API dokümantasyonu ve manuel endpoint testleri |
| **Black**              | Python kod biçimlendirme                                |
| **Git / GitHub**       | Sürüm kontrolü ve kaynak kod yönetimi                   |

### Geliştirme Ortamı

Uygulama Python sanal ortamı içerisinde çalıştırılmaktadır.

Uygulama bağımlılıkları:

```text
requirements.txt
```

## 10. Genel Veri Akışı

API içerisindeki temel işlemler aşağıdaki akışlarla gerçekleştirilir.

### Tek Event Oluşturma Akışı

```text
İstemci POST /events/ isteği
        ↓
X-API-Key doğrulaması
        ↓
Pydantic GameEvent doğrulaması
        ↓
Kategori ve event_data eşleşme kontrolü
        ↓
SQLAlchemy GameEvent nesnesinintext
İstemci POST /events/ isteği
        ↓
X-API-Key doğrulaması
        ↓
Pydantic GameEvent oluşturulması
        ↓
Veritabanına kayıt
        ↓
Transaction commit
        ↓
EventResponse doğrulaması
        ↓
201 Created cevabı
```

Pydantic doğrulaması başarısız olursa veritabanı işlemine geçilmeden `422` cevabı döndürülür.

API anahtarı eksik veya geçersizse istek `401 Unauthorized` ile durdurulur.

SQLAlchemy kaynaklı bir veritabanı hatasında transaction geri alınır ve `500 Internal Server Error` cevabı döndürülür.

---

### Batch Event Oluşturma Akışı

```text
İstemci POST /events/batch isteği
        ↓
X-API-Key doğrulaması
        ↓
BatchEventCreateRequest doğrulaması
        ↓
Batch içerisindeki tüm GameEvent nesnelerinin doğrulanması
        ↓
Kategori ve event_data eşleşmelerinin kontrolü
        ↓
SQLAlchemy GameEvent nesnelerinin oluşturulması
        ↓
Toplu veritabanı işlemi
        ↓
Transaction commit
        ↓
BatchEventCreateResponse
        ↓
201 Created cevabı
```

Batch içerisindeki eventlerden herhangi biri Pydantic doğrulamasından geçemezse endpoint çalıştırılmaz ve hiçbir event veritabanına kaydedilmez.

Batch isteği en az `1`, en fazla `100` event içerebilir.

---

### Event Sorgulama Akışı

`GET /events/` isteğinde genel akış:

```text
İstemci GET /events/ isteği
        ↓
X-API-Key doğrulaması
        ↓
Query parametrelerinin doğrulanması
        ↓
Kategori ve tarih filtrelerinin uygulanması
        ↓
Filtrelere uyan toplam kayıt sayısının hesaplanması
        ↓
Sayfalama uygulanması
        ↓
Eventlerin veritabanından alınması
        ↓
EventListResponse
        ↓
200 OK cevabı
```

Desteklenen sorgu parametreleri:

```text
category
date_from
date_to
skip
limit
```

`date_from` değeri `date_to` değerinden sonra ise istek `422` ile reddedilir.

---

### Kullanıcıya Göre Event Sorgulama Akışı

```text
İstemci GET /events/user/{user_id} isteği
        ↓
X-API-Key doğrulaması
        ↓
Pagination parametrelerinin doğrulanması
        ↓
user_id filtresinin uygulanması
        ↓
Toplam kayıt sayısının hesaplanması
        ↓
Sayfalama uygulanması
        ↓
UserEventListResponse
        ↓
200 OK cevabı
```

Belirtilen `user_id` değerine ait kayıt bulunmaması hata olarak değerlendirilmez. Bu durumda boş `data` listesi ve `200 OK` cevabı döndürülür.

---

### İstatistik Sorgulama Akışı

İstatistik endpointleri de API anahtarıyla korunur.

Günlük event istatistiklerinde:

```text
GET /stats/daily-events
        ↓
X-API-Key doğrulaması
        ↓
Eventlerin tarihe göre gruplanması
        ↓
Her gün için event sayısının hesaplanması
        ↓
DailyEventStatsResponse
        ↓
200 OK
```

Aktif kullanıcı istatistiklerinde:

```text
GET /stats/active-users
        ↓
X-API-Key doğrulaması
        ↓
Opsiyonel tarih filtrelerinin doğrulanması
        ↓
Tarih filtrelerinin uygulanması
        ↓
Distinct user_id değerlerinin sayılması
        ↓
ActiveUserStatsResponse
        ↓
200 OK
```

Aynı kullanıcının birden fazla eventi bulunsa bile aktif kullanıcı hesabında kullanıcı yalnızca bir kez sayılır.

---

### Loglama Akışı

Başarılı API ve veritabanı işlemleri yapılandırılmış biçimde loglanır.

Temel log seviyeleri:

```text
INFO     → başarılı işlemler ve sorgular
WARNING  → geçersiz veya eksik API key denemeleri
ERROR    → sunucu ve veritabanı hataları
```

Terminalde okunabilir log formatı kullanılırken uygulama logları ayrıca JSON biçiminde:

```text
logs/app.json
```

dosyasına yazılır.

Güvenlik nedeniyle gerçek API anahtarı log kayıtlarına dahil edilmez.
