## API Tasarım Dokümanı - Startgate Telemetry API

Bu doküman, oyunlardan gelen telemetri olaylarını (events) toplamak, doğrulamak ve sorgulanabilir kılmak amacıyla geliştirilen servisin uç noktalarını (endpoints) ve veri şemalarını tanımlar.

## 1. Uç Noktalar (Endpoints)

Sistem, RESTful standartlarına uygun olarak aşağıdaki uç noktaları sağlamaktadır:

**GET /health**

İşlev: API'nin ayakta ve çalışır durumda olup olmadığını kontrol eder.

Yanıt: 200 OK ({"status": "ok", "message": "Service is healthy"})

**POST /events**

İşlev: Oyun istemcisinden gelen yeni telemetri olaylarını kabul eder, Pydantic kurallarına göre doğrular ve veritabanına yazar.

Gövde (Body): GameEvent JSON formatı.

Yanıt: Başarılı kayıtta 201 Created. Doğrulama hatasında 422 Unprocessable Entity.

**GET /events (Sayfalama Desteği)**

İşlev: Veritabanına kaydedilmiş tüm olayları listeler. Performans için skip ve limit parametreleri ile sayfalama (pagination) yapar.

Yanıt: 200 OK (Toplam kayıt sayısı ve olayların listesi).

**GET /events/user/{user_id}**

İşlev: Sistemdeki belirli bir oyuncuya (user_id) ait olan tüm olay geçmişini filtreler ve döndürür.

Yanıt: 200 OK (Kullanıcıya ait olayların listesi).

## 2. Olay Şeması (Event Schema)

Uygulamaya gönderilen veriler (payload), oyun analitiği standartlarına uygun olarak katı bir JSON şemasına (Pydantic) tabi tutulmaktadır.

**Ortak Alanlar (Common Fields)**
Her olay isteğinde aşağıdaki temel alanların gönderilmesi zorunludur:

_timestamp_: Etkinlik zamanı (UTC).

_category_: Olayın ana kategorisi (business, progression, design, resource, error, user, session_end, ad, impression, info).

_platform:_ Kullanıcı platformu (iOS, Android, Web).

_os_version:_ İşletim sistemi sürümü.

_device / manufacturer:_ Cihaz modeli ve üreticisi.

_client_ts:_ İstemci tarafındaki Unix zaman damgası.

_user_id / session_id:_ Oyuncu ve oturumun benzersiz kimlikleri.

_session_num:_ Kullanıcının toplam oturum sayısı (0'dan büyük olmalıdır).

_sdk_version / v:_ Kullanılan SDK ve Oyun versiyonu.

## Dinamik Alt Şemalar (event_data)

category alanında belirtilen tipe göre, event_data objesinin içindeki yapı dinamik olarak değişir ve doğrulanır.

**Temel alt şema örnekleri:**

_BusinessData:_ Gerçek para harcamalarını takip eder. (currency [örn: USD, TRY], amount, cart_type zorunludur).

_ProgressionData:_ Oyuncunun bölüm/görev ilerlemesini takip eder. (status [Start, Complete, Fail], progression_01 zorunludur).

_ResourceData:_ Oyun içi sanal ekonomi akışını (altın, elmas kazanımı/harcanması) takip eder. (flow_type [Sink, Source], item_type, amount zorunludur).

_ErrorData:_ Oyun içi hataları loglar. (severity, message zorunludur).

Şemada tanımlanmayan ekstra hiçbir verinin kabul edilmemesi için _extra: forbid_ kuralı uygulanmaktadır.
