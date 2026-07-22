from pydantic import BaseModel, Field
from typing import Optional, Union, Literal
from datetime import datetime

# --- ALT ŞEMALAR (EVENT DATA) ---

class BusinessData(BaseModel):
    currency: str = Field(..., description="Para birimi (örn: USD, TRY)")
    amount: int = Field(..., description="Miktar (kuruş/cent cinsinden)")
    cart_type: Optional[str] = Field(None, description="Satın alımın yapıldığı yer (örn: shop, end_of_level)")

class ProgressionData(BaseModel):
    status: Literal["Start", "Complete", "Fail"] = Field(..., description="Bölüm/Görev durumu")
    progression_01: str = Field(..., description="Ana bölüm adı (örn: level_01)")
    progression_02: Optional[str] = Field(None, description="Alt bölüm adı (örn: phase_1)")
    progression_03: Optional[str] = Field(None, description="Daha alt bölüm detayları")
    score: Optional[int] = Field(None, description="Bölüm sonu skoru")

class DesignData(BaseModel):
    event_id: str = Field(..., description="Tasarım olayının adı (örn: kill:boss, ui:click:play)")
    value: Optional[float] = Field(None, description="Olayla ilgili sayısal bir değer (örn: geçen süre, hasar)")

class ResourceData(BaseModel):
    flow_type: Literal["Sink", "Source"] = Field(..., description="Kaynak akış yönü (Sink: Harcama, Source: Kazanma)")
    currency: str = Field(..., description="Kaynak türü (örn: Gems, Gold)")
    item_type: str = Field(..., description="Öğenin kategorisi (örn: Weapons, Boosters)")
    item_id: str = Field(..., description="Spesifik öğe (örn: Sword_01, Health_Potion)")
    amount: float = Field(..., description="Kazanılan veya harcanan miktar")

class ErrorData(BaseModel):
    severity: Literal["debug", "info", "warning", "error", "critical"] = Field(..., description="Hata seviyesi")
    message: str = Field(..., description="Hata mesajı veya stack trace")


# --- ANA ŞEMA (GAME EVENT) ---

class GameEvent(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Etkinlik zamanı")
    category: Literal["business", "progression", "design", "resource", "error"] = Field(
        ..., description="Etkinlik kategorisi"
    )
    platform: str = Field(..., description="Kullanıcı platformu (örn: iOS, Android, Web)")
    os_version: str = Field(..., description="İşletim sistemi sürümü")
    device: str = Field(..., description="Cihaz modeli")
    client_ts: int = Field(..., description="İstemci tarafındaki Unix timestamp")
    user_id: str = Field(..., description="Benzersiz kullanıcı kimliği")
    session_id: str = Field(..., description="Oturum kimliği")
    session_num: int = Field(..., description="Kullanıcının toplam oturum sayısı")
    sdk_version: str = Field(..., description="Kullanılan SDK sürümü")
    manufacturer: str = Field(..., description="Cihaz üreticisi")
    v: str = Field(..., description="Oyun/Uygulama versiyonu")
    
    # Tüm alt şemaları Union ile birleştiriyoruz
    event_data: Union[BusinessData, ProgressionData, DesignData, ResourceData, ErrorData] = Field(
        ..., description="Kategoriye özel detaylı veriler"
    )