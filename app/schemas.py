from pydantic import BaseModel

class GameEvent(BaseModel):
    user_id: str
    session_id: str
    session_num: int
    platform: str
    os_version: str
    sdk_version: str
    device: str
    manufacturer: str
    client_ts: int
    v: str
    category: str