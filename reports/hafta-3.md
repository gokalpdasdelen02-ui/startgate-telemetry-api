# Hafta 3 Raporu – Test, Sorgulama ve Özet İstatistikler

## Haftanın Hedefi

Bu hafta telemetri API servisinin güvenilirliğini artırmak, olayları daha gelişmiş biçimde sorgulamak ve verilerden temel istatistikler üretmek amaçlandı.

## Yapimde sorgulamak ve verilerden temel istatistikler üretmek amaçlandı.

## Yapılan Çalışmalar

### 1. Otomatik API Testleri

API endpointleri için `pytest` ve FastAPI `TestClient` kullanılarak otomatik testler geliştirildi.

Testlerde her senaryo için geçici ve bağımsız bir SQLite veritabanı oluşturuldu. Böylece testler gerçek geliştirme veritabanını değiştirmeden ve birbirlerini etkilemeden çalışmaktadır.

Test edilen başlıca senaryolar:

- Sağlık endpointi
- Başarılı event kaydı
- Eksik ve yanlış API key
- Event listeleme
- Kullanıcıya göre event listeleme
- Bilinmeyen kullanıcı için boş sonuç
- Pydantic alan ve veri tipi doğrulamaları
- Kategori ve `event_data` modeli eşleşmesi
- Genel ve kullanıcıya özel sayfalama
- Batch event kaydı
- Boş batch listesinin reddedilmesi
- Geçersiz event içeren batch isteğinde hiçbir kaydın oluşturulmaması
- Kategori filtreleme
- Tarih aralığı filtreleme
- Ters tarih aralığının reddedilmesi
- Günlük event istatistikleri
- Benzersiz aktif kullanıcı sayısı
- Aktif kullanıcıların tarih aralığına göre filtrelenmesi

Hafta sonunda toplam 36 test başarılı şekilde çalışmaktadır.

```text
36 passed
```

### 2. Test Kapsam Raporu

Test kapsamını ölçmek için `pytest-cov` kullanıldı.

Coverage raporu şu komutla oluşturuldu:

```bash
python -m pytest --cov=app --cov-report=term-missing
```

Toplam test kapsamı:

```text
89%
```

Coverage dışında kalan bölümlerin önemli kısmı, kasıtlı veritabanı hatası oluşturulmasını gerektiren hata yönetimi ve rollback dallarından oluşmaktadır.

### 3. Batch Event Kaydı

Tek istekte birden fazla telemetri olayının gönderilebilmesi için şu endpoint geliştirildi:

```text
POST /events/batch
```

Batch endpointi:

- Tek istekte 1–100 event kabul eder.
- Bütün eventleri Pydantic ile doğrular.
- Kayıtları tek transaction içinde veritabanına ekler.
- Veritabanı hatasında rollback uygular.
- Oluşturulan event sayısını ve eventleri cevapta döndürür.

Batch içindeki eventlerden biri doğrulamadan geçemezse istek tamamen reddedilir ve hiçbir event kaydedilmez.

### 4. Event Filtreleme

Genel event sorgusuna kategori ve tarih filtreleri eklendi.

Desteklenen parametreler:

```text
category
date_from
date_to
skip
limit
```

Örnek:

```text
GET /events/?category=business&date_from=2026-08-01T00:00:00Z&date_to=2026-08-06T23:59:59Z&skip=0&limit=10
```

Başlangıç tarihi bitiş tarihinden sonra gönderildiğinde API `422` durum kodu döndürmektedir.

### 5. Sayfalama

Genel event sorgusunda ve kullanıcıya özel event sorgusunda `skip` ve `limit` parametreleri kullanılmaktadır.

Kurallar:

- `skip` sıfır veya daha büyük olmalıdır.
- `limit` 1–100 arasında olmalıdır.
- Cevapta toplam kayıt sayısı ve mevcut sayfadaki kayıt sayısı ayrı olarak gösterilir.

### 6. Günlük Event İstatistikleri

Eventleri günlere göre gruplandırarak sayılarını döndüren endpoint geliştirildi:

```text
GET /stats/daily-events
```

Örnek cevap:

```json
{
  "status": "success",
  "data": [
    {
      "date": "2026-08-06",
      "event_count": 5
    }
  ]
}
```

### 7. Aktif Kullanıcı İstatistikleri

En az bir event gönderen benzersiz kullanıcıların sayısını döndüren endpoint geliştirildi:

```text
GET /stats/active-users
```

Endpoint isteğe bağlı olarak `date_from` ve `date_to` parametrelerini desteklemektedir.

Aynı kullanıcının birden fazla eventi olsa bile kullanıcı yalnızca bir kez sayılır.

### 8. Yapılandırılmış Loglama

Loglama için Loguru kütüphanesi kullanıldı.

Başarılı işlemler `INFO`, geçersiz API key denemeleri `WARNING`, sunucu veya veritabanı hataları `ERROR` seviyesinde kaydedilmektedir.

Eklenen başlıca log olayları:

```text
event_created
batch_events_created
events_queried
user_events_queried
daily_event_stats_queried
active_user_stats_queried
api_key_authentication_failed
api_key_configuration_missing
database_error
```

Terminalde insan tarafından okunabilir log formatı kullanılmaktadır. Aynı loglar `logs/app.json` dosyasına yapılandırılmış JSON biçiminde yazılmaktadır.

Güvenlik nedeniyle API anahtarının gerçek değeri loglara kaydedilmemektedir.

### 9. API Key Koruması

Sağlık kontrolü dışındaki event ve istatistik endpointleri `X-API-Key` headerı ile korunmaktadır.

Eksik veya yanlış API key gönderildiğinde:

```text
401 Unauthorized
```

durum kodu dönmektedir.

## Kullanılan Teknolojiler

- FastAPI
- Pydantic
- SQLAlchemy
- SQLite
- pytest
- HTTPX TestClient
- pytest-cov
- Loguru
- Uvicorn

## Hafta Sonu Sonucu

Hafta 3 sonunda:

- Batch event kaydı tamamlandı.
- Pagination ve filtreleme tamamlandı.
- Günlük event ve aktif kullanıcı istatistikleri eklendi.
- Yapılandırılmış loglama tamamlandı.
- 36 otomatik test başarıyla çalıştırıldı.
- Toplam test kapsamı `%89` seviyesine ulaştı.
- README güncel endpointler, testler ve kullanım örnekleriyle güncellendi.

Proje, Hafta 4 kapsamında Docker, son dokümantasyon ve teslim hazırlıklarına geçmeye hazır hâle getirildi.
