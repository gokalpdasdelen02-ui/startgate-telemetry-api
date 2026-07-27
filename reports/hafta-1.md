# Hafta 1 Durum Raporu

**Proje:** Oyun Telemetri API Servisi  
**Tarih:** 24 Temmuz 2026

## Bu Hafta Tamamlananlar

- Proje klasör yapısı, Git deposu ve sanal ortam oluşturuldu. Projenin gerekli paketleri `requirements.txt` dosyasına kaydedildi.
- FastAPI uygulaması kuruldu ve servisin çalışıp çalışmadığını kontrol eden `GET /health` uç noktası geliştirildi.
- Oyunlardan gelen telemetri olaylarını kabul eden `POST /events` uç noktası oluşturuldu. Geçerli olaylar `201 Created` durum koduyla kabul edilmektedir.
- GameAnalytics yapısı temel alınarak 10 farklı olay kategorisi için Pydantic şemaları tasarlandı: `business`, `progression`, `design`, `resource`, `error`, `user`, `session_end`, `ad`, `impression` ve `info`.
- Verilerin bellekte tutulması yerine SQLAlchemy ORM ve SQLite kullanılarak kalıcı veritabanı yapısı kuruldu.
- Bütün olayları listeleyen `GET /events` ve belirli bir kullanıcıya ait olayları getiren `GET /events/user/{user_id}` uç noktaları geliştirildi.
- Listeleme uç noktalarına `skip` ve `limit` parametreleriyle sayfalama eklendi. Geçersiz değerlerin gönderilmesini önlemek için alt ve üst sınırlar tanımlandı.
- API cevapları Pydantic response modelleri ile standartlaştırıldı ve Swagger arayüzünde cevap yapılarının görüntülenmesi sağlandı.
- Swagger UI üzerinden başarılı ve hatalı istek senaryoları manuel olarak test edildi.

## Karşılaşılan Zorluklar ve Çözümler

### Kategori ve olay verisi uyumsuzluğu

**Zorluk:** `event_data` alanında kullanılan `Union`, verinin tanımlanan modellerden birine uyduğunu kontrol ediyor fakat olay kategorisiyle uyumunu garanti etmiyordu. Örneğin `business` kategorisi altında reklam verisi kabul edilebiliyordu.

**Çözüm:** `model_validator` kullanılarak her kategorinin yalnızca kendisine ait `event_data` modeliyle eşleşmesi sağlandı.

### Eksik SQLAlchemy bağımlılığı

**Zorluk:** SQLAlchemy projede kullanıldığı hâlde başlangıçta bağımlılık dosyasında bulunmuyordu.

**Çözüm:** SQLAlchemy sürümü `requirements.txt` dosyasına eklenerek projenin başka bir ortamda yeniden kurulabilir olması sağlandı.

### Veritabanı alanlarının boş bırakılabilmesi

**Zorluk:** SQLAlchemy modelinde bazı zorunlu alanlar veritabanı seviyesinde boş bırakılabiliyordu.

**Çözüm:** Zorunlu kolonlara `nullable=False` eklenerek veri bütünlüğü güçlendirildi.

## Alınan Teknik Kararlar ve Gerekçeleri

- **FastAPI:** Pydantic entegrasyonu, otomatik Swagger/OpenAPI dokümantasyonu ve hızlı API geliştirme imkânı nedeniyle tercih edildi.
- **Pydantic:** Gelen JSON verilerinin tiplerini, zorunlu alanlarını ve kategoriye özel kurallarını doğrulamak için kullanıldı.
- **SQLAlchemy ve SQLite:** İlk geliştirme aşamasında kolay kurulum ve kalıcı veri saklama sağladığı için kullanıldı.
- **Senkron yapı:** Mevcut SQLite bağlantısı ve SQLAlchemy Session yapısı senkron olduğu için endpointler normal `def` ile geliştirildi.
- **UTC zaman kullanımı:** Farklı cihazlardan gelen olay zamanlarını ortak bir standartta tutmak için UTC tercih edildi.
- **Sayfalama:** Veri miktarı arttığında bütün kayıtların tek istekte getirilmesini önlemek için `skip` ve `limit` kullanıldı.
- **Response modelleri:** API cevaplarının standartlaştırılması, doğrulanması ve Swagger dokümantasyonunda açık şekilde gösterilmesi için Pydantic response modelleri oluşturuldu.

## Gelecek Hafta Planı

- Yazma işlemlerini korumak için API key tabanlı temel kimlik doğrulama eklenmesi.
- Hata cevaplarının daha standart bir yapıya dönüştürülmesi.
- Veritabanı şemasının ve API kullanım örneklerinin dokümante edilmesi.
- README dosyasının güncel klasör yapısı ve uç noktalarla uyumlu hâle getirilmesi.
- İkinci hafta kapsamındaki veritabanı ve doğrulama çalışmalarının geliştirilmesi.
