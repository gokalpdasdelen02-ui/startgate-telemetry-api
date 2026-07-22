# Hafta 1 Durum Raporu

**Proje:** Telemetry API
**Tarih:** 24 Temmuz 2026

### Bu Hafta Tamamlananlar

- Proje klasör yapısı (`app/`, `tests/` ve `reports/`) ve sanal ortam (virtual environment) başarıyla kuruldu.
- GameAnalytics standartlarına uygun 10 farklı olay (event) kategorisi için Pydantic şemaları (`schemas.py`) tasarlandı.
- FastAPI iskeleti kurularak `GET /health` (nabız yoklaması) ve `POST /events` (veri alımı) uç noktaları oluşturuldu.
- Beklentilerin bir adım ötesine geçilerek, verilerin sadece bellekte (in-memory) tutulması yerine kalıcı bir SQLite veritabanı entegrasyonu (`database.py`, `models.py`) sağlandı.
- Swagger UI ve manuel Python scriptleri (requests) üzerinden API uç noktalarının başarılı bir şekilde çalıştığı ve veritabanına kayıt yaptığı test edildi.

### Karşılaşılan Zorluklar ve Çözümler

- **Zorluk:** `POST /events` testleri sırasında Swagger arayüzünün otomatik şablonunda, olay gövdesi (`event_data`) için varsayılan olarak parasal verilerin (BusinessData) çıkması kafa karışıklığı yarattı.
- **Çözüm:** Bunun Pydantic `Union` yapısının varsayılan listeleme davranışı olduğu anlaşıldı. Gerçekçi bir `ProgressionData` senaryosu (Seviye 5'i geçme) JSON olarak manuel girildiğinde, API'nin doğru modeli kendi kendine seçtiği ve veri kaybı olmadan veritabanına kaydettiği doğrulandı.
- **Zorluk:** İlk geliştirme aşamasında `main.py` içerisindeki veri kayıt fonksiyonunda kod tekrarları ve format hataları tespit edildi.
- **Çözüm:** Kod temizlenerek gereksiz tekrarlar giderildi ve başarılı işlem sonrası HTTP 200 durum kodu ile standart JSON yanıtı dönülmesi sağlandı.

### Alınan Teknik Kararlar ve Gerekçeleri

- **FastAPI Kullanımı:** Hızlı prototipleme imkanı sunması ve OpenAPI (Swagger) dokümantasyonunu otomatik üretmesi nedeniyle tercih edildi.
- **Pydantic Şemaları:** Dışarıdan (oyun motorundan) gelecek verilerin API'yi bozmaması ve katı doğrulama (validation) kurallarından geçmesi için uygulandı. `Union` veri tipi kullanılarak farklı olay türlerinin tek bir uç noktadan güvenle alınması sağlandı.
- **SQLite Tercihi:** İlk haftanın gereksinimi bellekte tutmak olsa da, projeyi gerçek dünya senaryolarına daha uygun hale getirmek ve kalıcı veri takibini şimdiden kurgulamak için yerel bir veritabanı dosyası kullanıldı.

### Gelecek Hafta Planı

- Uç noktaların kararlılığını kanıtlamak için `tests/` klasörü içerisine otomatik birim testlerinin (unit tests) yazılması.
- Toplanan telemetri verilerini filtrelemek veya analiz etmek için yeni GET uç noktalarının (örneğin, belirli bir kullanıcının geçmiş olaylarını listeleme) API'ye eklenmesi.
