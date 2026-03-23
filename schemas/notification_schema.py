from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NotificationCreate(BaseModel):
    user_id: str
    message: str
    created_at: Optional[datetime] = None
    is_read: bool = False

class NotificationOut(BaseModel):
    id: str
    user_id: str
    message: str
    created_at: Optional[datetime] = None
    is_read: bool = False