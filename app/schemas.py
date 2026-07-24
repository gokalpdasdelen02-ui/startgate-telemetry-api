from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union, Literal
from datetime import datetime

# --- ORTAK YAPILANDIRMA ---
class BaseEventData(BaseModel):
    #şemada tanımlanmayan verilerin gelmesini yasaklar 
    model_config = {"extra": "forbid"}

# --- ALT ŞEMALAR (EVENT DATA) ---

class BusinessData(BaseEventData):
    currency: str = Field(..., min_length=3, max_length=3, description="Para birimi (örn: USD, TRY)")
    amount: int = Field(..., gt=0, description="Miktar (kuruş/cent cinsinden)")
    cart_type: Optional[str] = Field(None, description="Satın alımın yapıldığı yer (örn: shop, end_of_level)")

    #para biriminin sadece büyük harf olmasını sağlıyoruz.
    @field_validator("currency")
    @classmethod
    def currency_must_be_uppercase(cls, v: str) -> str:
        if not v.isalpha() or not v.isupper():
            raise ValueError("Para birimi sadece üç büyük harften oluşmalıdır. (Örn: USD, TRY)")
        return v

class ProgressionData(BaseEventData):
    status: Literal["Start", "Complete", "Fail"] = Field(..., description="Bölüm/Görev durumu")
    progression_01: str = Field(..., description="Ana bölüm adı (örn: level_01)")
    progression_02: Optional[str] = Field(None, description="Alt bölüm adı (örn: phase_1)")
    progression_03: Optional[str] = Field(None, description="Daha alt bölüm detayları")
    score: Optional[int] = Field(None, description="Bölüm sonu skoru")

class DesignData(BaseEventData):
    event_id: str = Field(..., description="Tasarım olayının adı (örn: kill:boss, ui:click:play)")
    value: Optional[float] = Field(None, description="Olayla ilgili sayısal bir değer (örn: geçen süre, hasar)")

class ResourceData(BaseEventData):
    flow_type: Literal["Sink", "Source"] = Field(..., description="Kaynak akış yönü (Sink: Harcama, Source: Kazanma)")
    currency: str = Field(..., description="Kaynak türü (örn: Gems, Gold)")
    item_type: str = Field(..., description="Öğenin kategorisi (örn: Weapons, Boosters)")
    item_id: str = Field(..., description="Spesifik öğe (örn: Sword_01, Health_Potion)")
    amount: float = Field(..., gt=0, description="Kazanılan veya harcanan miktar 0'dan büyük olmalıdır.")

class ErrorData(BaseEventData):
    severity: Literal["debug", "info", "warning", "error", "critical"] = Field(..., description="Hata seviyesi")
    message: str = Field(..., description="Hata mesajı veya stack trace")

class UserData(BaseEventData):
    custom_01: Optional[str] = Field(None, description="Opsiyonel kullanıcı verisi")

class SessionEndData(BaseEventData):
    length: int = Field(...,gt=0, description="Oturumun uzunluğu (saniye cinsinden) sıfırdan büyük olmalıdır.")

class AdData(BaseEventData):
    ad_action: Literal["clicked", "show", "failed", "reward_received", "request"] = Field(
        ..., description="Kullanıcının reklamla etkileşimi"
    )
    ad_type: Literal["video", "rewarded_video", "playable", "interstitial", "banner"] = Field(
        ..., description="Reklamın formatı"
    )
    ad_sdk_name: str = Field(..., description="Reklam ağının adı (örn: admob, unityads)")
    ad_placement: str = Field(..., description="Reklamın çıktığı yer (örn: end_of_level)")  

class ImpressionData(BaseEventData):
    ad_network_name: str = Field(..., description="Gösterim yapan reklam ağı (örn: ironSource)")
    ad_network_version: str = Field(..., description="Reklam ağının SDK versiyonu")

class InfoData(BaseEventData):
    message: str = Field(..., description="Gönderilecek log veya bilgi mesajı")

# --- ANA ŞEMA (GAME EVENT) ---

class GameEvent(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Etkinlik zamanı")
    category: Literal["business", "progression", "design", "resource", "error","user","session_end","ad","impression","info"] = Field(
        ..., description="Etkinlik kategorisi"
    )
    platform: str = Field(..., description="Kullanıcı platformu (örn: iOS, Android, Web)")
    os_version: str = Field(..., description="İşletim sistemi sürümü")
    device: str = Field(..., description="Cihaz modeli")
    client_ts: int = Field(..., description="İstemci tarafındaki Unix timestamp")
    user_id: str = Field(..., description="Benzersiz kullanıcı kimliği")
    session_id: str = Field(..., description="Oturum kimliği")
    session_num: int = Field(..., gt=0,description="Kullanıcının toplam oturum sayısı (0'dan büyük olmalıdır)")
    sdk_version: str = Field(..., description="Kullanılan SDK sürümü")
    manufacturer: str = Field(..., description="Cihaz üreticisi")
    v: str = Field(..., description="Oyun/Uygulama versiyonu")
    
    # Tüm alt şemaları Union ile birleştiriyoruz
    event_data: Union[BusinessData, ProgressionData, DesignData, ResourceData, ErrorData, UserData, SessionEndData, AdData, ImpressionData, InfoData] = Field(
        ..., description="Kategoriye özel detaylı veriler"
    )