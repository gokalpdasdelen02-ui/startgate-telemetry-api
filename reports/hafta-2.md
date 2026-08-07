# Hafta 2 Raporu – Veritabanı, CRUD ve Doğrulama

## Haftanın Hedefi

Bu hafta telemetri API servisinde olayların yalnızca geçici olarak alınması yerine kalıcı olarak veritabanında saklanması, kaydedilen olayların tekrar sorgulanabilmesi ve gelen verilerin daha güvenli şekilde doğrulanması amaçlandı.

Bu kapsamda SQLAlchemy ile veritabanı katmanı oluşturuldu, event endpointleri veritabanına bağlandı, Pydantic doğrulamaları geliştirildi ve temel API key kontrolü eklendi.

## Yapılan Çalışmalar

### 1. Veritabanı Altyapısının Oluşturulması

Projenin kalıcı veri saklama katmanı için SQLAlchemy ve SQLite kullanıldı.

`app/database.py` içerisinde:

- SQLAlchemy engine oluşturuldu.
- Session yönetimi yapılandırıldı.
- ORM modellerinin kullanacağı `Base` sınıfı tanımlandı.
- FastAPI endpointlerinde kullanılmak üzere `get_db()` dependency'si oluşturuldu.

Bu yapı sayesinde endpointler doğrudan veritabanı oturumuna erişebilir hâle getirildi.

### 2. GameEvent Veritabanı Modelinin Tasarlanması

Telemetri eventlerinin veritabanında saklanabilmesi için SQLAlchemy tabanlı `GameEvent` modeli oluşturuldu.

Modelde başlıca şu alanlar bulunmaktadır:

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

Sık sorgulanabilecek bazı alanlarda index kullanılarak ileride yapılacak sorgular için uygun bir yapı oluşturuldu.

`event_data` alanı farklı event kategorilerinin değişken veri yapılarını destekleyebilmek amacıyla JSON olarak saklandı.

### 3. Event Kaydetme Endpointinin Veritabanına Bağlanması

Tek bir telemetri eventinin kaydedilmesi için:

```text
POST /events/
```

endpointi veritabanına bağlandı.

İstek Pydantic tarafından doğrulandıktan sonra gelen veri SQLAlchemy `GameEvent` modeline dönüştürülerek veritabanına kaydedilmektedir.

Başarılı kayıt sonucunda API oluşturulan eventin veritabanı kimliğini ve diğer bilgilerini cevap olarak döndürmektedir.

Başarılı kayıt için:

```text
201 Created
```

durum kodu kullanılmaktadır.

Veritabanı işlemi sırasında hata oluşması durumunda transaction geri alınarak:

```python
db.rollback()
```

işlemi uygulanmaktadır.

### 4. Event Listeleme Endpointinin Oluşturulması

Veritabanına kaydedilen eventlerin tekrar sorgulanabilmesi için:

```text
GET /events/
```

endpointi oluşturuldu.

Bu endpoint veritabanındaki eventleri okuyarak API cevabı olarak döndürmektedir.

Böylece sistem yalnızca event alan bir servis olmaktan çıkarak kaydedilmiş telemetri verilerinin tekrar sorgulanabildiği bir yapıya dönüştürüldü.

### 5. Kullanıcıya Göre Event Sorgulama

Belirli bir kullanıcıya ait telemetri eventlerini sorgulamak için:

```text
GET /events/user/{user_id}
```

endpointi oluşturuldu.

Bu endpoint yalnızca verilen `user_id` değerine ait kayıtları döndürmektedir.

Kullanıcıya ait event bulunmadığında hata üretmek yerine başarılı cevap içerisinde boş liste dönmesi tercih edildi.

### 6. Pydantic ile Katı Veri Doğrulama

Gelen event verilerinin güvenli ve beklenen yapıda olması için Pydantic şemaları geliştirildi.

Ana event modeli içerisinde ortak telemetri alanları tanımlandı ve farklı event kategorileri için ayrı `event_data` modelleri kullanıldı.

Desteklenen kategoriler:

```text
business
progression
design
resource
error
user
session_end
ad
impression
info
```

Kategoriye göre farklı veri modelleri kullanılarak her event türünün kendi alanları doğrulanmaktadır.

### 7. Category ve Event Data Eşleşme Kontrolü

Bir eventin `category` alanı ile gönderilen `event_data` modelinin birbiriyle uyumlu olması sağlandı.

Örneğin:

```text
category = business
```

olan bir eventin `BusinessData` yapısına uygun veri taşıması gerekmektedir.

Kategori ile gönderilen veri modeli uyuşmadığında istek doğrulamadan geçmemektedir.

Bu kontrol Pydantic `model_validator` kullanılarak gerçekleştirildi.

### 8. Alan Doğrulama Kuralları

Event şemalarında çeşitli veri doğrulama kuralları uygulandı.

Başlıca kontroller:

- Zorunlu alanların bulunması
- Fazladan alanların reddedilmesi
- `session_num` değerinin sıfırdan büyük olması
- `client_ts` değerinin negatif olmaması
- Miktar alanlarının sıfırdan büyük olması
- Para biriminin üç büyük alfabetik karakterden oluşması
- Event kategorilerinin izin verilen değerlerden biri olması
- Event tipine özel alanların doğrulanması

Geçersiz veriler FastAPI/Pydantic tarafından:

```text
422 Unprocessable Content
```

durum koduyla reddedilmektedir.

### 9. Response Modellerinin Oluşturulması

API cevaplarının standart bir yapıda kalması için Pydantic response modelleri oluşturuldu.

Kullanılan temel response modelleri:

- `EventResponse`
- `EventCreateResponse`
- `EventListResponse`
- `UserEventListResponse`

Bu modeller sayesinde API cevaplarının Swagger/OpenAPI üzerinde açık şekilde gösterilmesi ve SQLAlchemy nesnelerinin kontrollü biçimde JSON çıktısına dönüştürülmesi sağlandı.

### 10. API Key ile Temel Kimlik Doğrulama

API'ye izinsiz event gönderilmesini engellemek amacıyla `X-API-Key` tabanlı basit kimlik doğrulama mekanizması oluşturuldu.

API anahtarı HTTP header içerisinde gönderilmektedir:

```text
X-API-Key: your-secret-api-key
```

Anahtar uygulama kodunun içine yazılmak yerine `.env` dosyasından okunmaktadır.

Gönderilen anahtar ile sunucudaki anahtar karşılaştırılarak geçersiz veya eksik anahtar durumunda:

```text
401 Unauthorized
```

cevabı dönmektedir.

Anahtar karşılaştırmasında güvenli karşılaştırma amacıyla `secrets.compare_digest()` kullanıldı.

### 11. Ortam Değişkenlerinin Yapılandırılması

Gizli ve ortama bağlı ayarların koddan ayrılması için `.env` tabanlı yapılandırma kullanıldı.

Başlıca ortam değişkenleri:

```text
TELEMETRY_API_KEY
DATABASE_URL
```

Gerçek `.env` dosyasının Git reposuna eklenmemesi sağlandı ve örnek yapılandırma için `.env.example` kullanıldı.

### 12. Veritabanı Şema Dokümantasyonu

Veritabanı modelinin daha anlaşılır olması için şema dokümantasyonu hazırlandı.

Dokümantasyonda:

- Event tablosundaki kolonlar
- Veri tipleri
- Zorunlu alanlar
- Index kullanılan alanlar
- JSON olarak saklanan `event_data`
- Model tasarım kararları

açıklandı.

İlgili doküman:

```text
docs/veritabani-semasi.md
```

### 13. Swagger ve HTTP Üzerinden Manuel Kontroller

Geliştirilen endpointler FastAPI'nin otomatik Swagger arayüzü üzerinden manuel olarak kontrol edildi.

Başlıca kontroller:

- Geçerli event gönderilmesi
- Eventin veritabanına kaydedilmesi
- Kaydedilen eventlerin tekrar sorgulanması
- Kullanıcıya göre event sorgulanması
- Hatalı verilerin `422` ile reddedilmesi
- Eksik veya yanlış API key kullanımının reddedilmesi

Swagger arayüzü:

```text
http://127.0.0.1:8000/docs
```

üzerinden kullanıldı.

## Hafta 2 Sonunda Kullanılabilen Temel Endpointler

```text
GET  /health
POST /events/
GET  /events/
GET  /events/user/{user_id}
```

## Kullanılan Teknolojiler

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite
- Uvicorn
- Swagger / OpenAPI
- python-dotenv / ortam değişkenleri

## Hafta Sonu Sonucu

Hafta 2 sonunda:

- Veritabanı şeması tasarlandı.
- SQLAlchemy ORM modeli oluşturuldu.
- SQLite veritabanı uygulamaya bağlandı.
- Event kaydetme işlemi kalıcı hâle getirildi.
- Kaydedilen eventlerin sorgulanması sağlandı.
- Kullanıcıya göre event sorgulama eklendi.
- Pydantic doğrulamaları geliştirildi.
- Kategori ile event verisi eşleşme kontrolü eklendi.
- API cevapları için response modelleri oluşturuldu.
- API key tabanlı temel erişim kontrolü eklendi.
- Veritabanı hataları için rollback mekanizması uygulandı.
- Veritabanı şema dokümantasyonu hazırlandı.
- Endpointler Swagger üzerinden manuel olarak doğrulandı.

Bu çalışmalar sonucunda proje, veriyi kalıcı olarak saklayan, doğrulayan ve tekrar sorgulayabilen bir CRUD API hâline getirildi ve Hafta 3'te yapılacak otomatik test, gelişmiş sorgulama, batch işlemleri ve istatistik çalışmalarına hazırlandı.
