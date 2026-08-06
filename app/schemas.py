from datetime import date, datetime, timezone
from typing import Optional, Union, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ORTAK YAPILANDIRMA
class BaseEventData(BaseModel):
    # şemada tanımlanmayan verilerin gelmesini yasaklar
    model_config = {"extra": "forbid"}

    # alt şemalar için değerler
    @field_validator("*", mode="before", check_fields=False)
    @classmethod
    def text_fields_must_not_be_blank(cls, value):
        if isinstance(value, str):
            stripped_value = value.strip()

            if not stripped_value:
                raise ValueError("Metin alanları boş bırakılamaz.")

            return stripped_value

        return value


# ALT ŞEMALAR


class BusinessData(BaseEventData):
    currency: str = Field(
        ..., min_length=3, max_length=3, description="Para birimi (örn: USD, TRY)"
    )
    amount: int = Field(..., gt=0, description="Miktar (kuruş/cent cinsinden)")
    cart_type: Optional[str] = Field(
        None,
        min_length=1,
        description="Satın alımın yapıldığı yer (örn: shop, end_of_level)",
    )

    # para biriminin sadece büyük harf olmasını sağlıyoruz.
    @field_validator("currency")
    @classmethod
    def currency_must_be_uppercase(cls, v: str) -> str:
        if not v.isalpha() or not v.isupper():
            raise ValueError(
                "Para birimi sadece üç büyük harften oluşmalıdır. (Örn: USD, TRY)"
            )
        return v


class ProgressionData(BaseEventData):
    status: Literal["Start", "Complete", "Fail"] = Field(
        ..., description="Bölüm/Görev durumu"
    )
    progression_01: str = Field(
        ..., min_length=1, description="Ana bölüm adı (örn: level_01)"
    )
    progression_02: Optional[str] = Field(
        None, min_length=1, description="Alt bölüm adı (örn: phase_1)"
    )
    progression_03: Optional[str] = Field(
        None, min_length=1, description="Daha alt bölüm detayları"
    )
    score: Optional[int] = Field(None, description="Bölüm sonu skoru")


class DesignData(BaseEventData):
    event_id: str = Field(
        ...,
        min_length=1,
        description="Tasarım olayının adı (örn: kill:boss, ui:click:play)",
    )
    value: Optional[float] = Field(
        None, description="Olayla ilgili sayısal bir değer (örn: geçen süre, hasar)"
    )


class ResourceData(BaseEventData):
    flow_type: Literal["Sink", "Source"] = Field(
        ..., description="Kaynak akış yönü (Sink: Harcama, Source: Kazanma)"
    )
    currency: str = Field(
        ..., min_length=1, description="Kaynak türü (örn: Gems, Gold)"
    )
    item_type: str = Field(
        ..., min_length=1, description="Öğenin kategorisi (örn: Weapons, Boosters)"
    )
    item_id: str = Field(
        ..., min_length=1, description="Spesifik öğe (örn: Sword_01, Health_Potion)"
    )
    amount: float = Field(
        ..., gt=0, description="Kazanılan veya harcanan miktar 0'dan büyük olmalıdır."
    )


class ErrorData(BaseEventData):
    severity: Literal["debug", "info", "warning", "error", "critical"] = Field(
        ..., description="Hata seviyesi"
    )
    message: str = Field(..., min_length=1, description="Hata mesajı veya stack trace")


class UserData(BaseEventData):
    custom_01: Optional[str] = Field(
        None, min_length=1, description="Opsiyonel kullanıcı verisi"
    )


class SessionEndData(BaseEventData):
    length: int = Field(
        ...,
        gt=0,
        description="Oturumun uzunluğu (saniye cinsinden) sıfırdan büyük olmalıdır.",
    )


class AdData(BaseEventData):
    ad_action: Literal["clicked", "show", "failed", "reward_received", "request"] = (
        Field(..., description="Kullanıcının reklamla etkileşimi")
    )
    ad_type: Literal[
        "video", "rewarded_video", "playable", "interstitial", "banner"
    ] = Field(..., description="Reklamın formatı")
    ad_sdk_name: str = Field(
        ..., min_length=1, description="Reklam ağının adı (örn: admob, unityads)"
    )
    ad_placement: str = Field(
        ..., min_length=1, description="Reklamın çıktığı yer (örn: end_of_level)"
    )


class ImpressionData(BaseEventData):
    ad_network_name: str = Field(
        ..., min_length=1, description="Gösterim yapan reklam ağı (örn: ironSource)"
    )
    ad_network_version: str = Field(
        ..., min_length=1, description="Reklam ağının SDK versiyonu"
    )


class InfoData(BaseEventData):
    message: str = Field(
        ..., min_length=1, description="Gönderilecek log veya bilgi mesajı"
    )


# ANA ŞEMA (GAME EVENT)


class GameEvent(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
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
                        "cart_type": "shop",
                    },
                }
            ]
        },
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Etkinlik Zamanı",
    )
    category: Literal[
        "business",
        "progression",
        "design",
        "resource",
        "error",
        "user",
        "session_end",
        "ad",
        "impression",
        "info",
    ] = Field(..., description="Etkinlik kategorisi")
    platform: str = Field(
        ..., min_length=1, description="Kullanıcı platformu (örn: iOS, Android, Web)"
    )
    os_version: str = Field(..., min_length=1, description="İşletim sistemi sürümü")
    device: str = Field(..., min_length=1, description="Cihaz modeli")
    client_ts: int = Field(..., ge=0, description="İstemci tarafındaki Unix timestamp")
    user_id: str = Field(..., min_length=1, description="Benzersiz kullanıcı kimliği")
    session_id: str = Field(..., min_length=1, description="Oturum kimliği")
    session_num: int = Field(
        ...,
        gt=0,
        description="Kullanıcının toplam oturum sayısı (0'dan büyük olmalıdır)",
    )
    sdk_version: str = Field(..., min_length=1, description="Kullanılan SDK sürümü")
    manufacturer: str = Field(..., min_length=1, description="Cihaz üreticisi")
    v: str = Field(..., min_length=1, description="Oyun/Uygulama versiyonu")

    # Tüm alt şemaları Union ile birleştiriyoruz

    event_data: Union[
        BusinessData,
        ProgressionData,
        DesignData,
        ResourceData,
        ErrorData,
        UserData,
        SessionEndData,
        AdData,
        ImpressionData,
        InfoData,
    ] = Field(..., description="Kategoriye özel detaylı veriler")

    @field_validator(
        "platform",
        "os_version",
        "device",
        "user_id",
        "session_id",
        "sdk_version",
        "manufacturer",
        "v",
    )
    @classmethod
    def text_fields_must_not_be_blank(cls, value: str) -> str:
        stripped_value = value.strip()

        if not stripped_value:
            raise ValueError("Bu alan boş bırakılamaz.")

        return stripped_value

    @model_validator(mode="after")
    def validate_event_data_matches_category(self):
        category_model_map = {
            "business": BusinessData,
            "progression": ProgressionData,
            "design": DesignData,
            "resource": ResourceData,
            "error": ErrorData,
            "user": UserData,
            "session_end": SessionEndData,
            "ad": AdData,
            "impression": ImpressionData,
            "info": InfoData,
        }

        expected_model = category_model_map[self.category]

        if not isinstance(self.event_data, expected_model):
            raise ValueError(
                f"'{self.category}' kategorisi için event_data "
                f"{expected_model.__name__} yapısında olmalıdır."
            )

        return self


class BatchEventCreateRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
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
                            "event_data": {"message": "Birinci batch test eventi"},
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
                                "cart_type": "shop",
                            },
                        },
                    ]
                }
            ]
        },
    )

    events: list[GameEvent] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Tek istekte kaydedilecek etkinlikler.",
    )


# CEVAP ŞEMASI
class EventResponse(GameEvent):
    model_config = ConfigDict(from_attributes=True)

    id: int


class EventCreateResponse(BaseModel):
    status: Literal["success"]
    message: str
    data: EventResponse


class BatchEventCreateResponse(BaseModel):
    status: Literal["success"]
    message: str
    created_count: int = Field(
        ...,
        ge=1,
        le=100,
        description="Başarıyla kaydedilen etkinlik sayısı",
    )
    data: list[EventResponse] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Veritabanına kaydedilen etkinlikler",
    )


class DailyEventCount(BaseModel):
    date: date
    event_count: int = Field(
        ...,
        ge=0,
        description="Belirlenen gündeki toplam etkinlil sayısı",
    )


class DailyEventStatsResponse(BaseModel):
    status: Literal["success"]
    data: list[DailyEventCount]


class ActiveUserStatsResponse(BaseModel):
    status: Literal["success"]
    active_users: int = Field(
        ...,
        ge=0,
        description="En az bir etkinlik gönderen kullanıcı sayısı",
    )


class EventListResponse(BaseModel):
    status: Literal["success"]
    total: int = Field(..., ge=0)
    count: int = Field(..., ge=0)
    skip: int = Field(..., ge=0)
    limit: int = Field(..., ge=1, le=100)
    data: list[EventResponse]


class UserEventListResponse(BaseModel):
    status: Literal["success"]
    user_id: str
    total: int = Field(..., ge=0)
    count: int = Field(..., ge=0)
    skip: int = Field(..., ge=0)
    limit: int = Field(..., ge=1, le=100)
    data: list[EventResponse]
