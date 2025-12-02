from typing import Optional
from pydantic import BaseModel


class UserRequest(BaseModel):
    user_id: str
    audio_link: Optional[str] = None
    text: Optional[str] = None
    audio: Optional[str] = None
    is_catalogue_mode : bool
    
class DeletePrevConv(BaseModel):
    user_id: str