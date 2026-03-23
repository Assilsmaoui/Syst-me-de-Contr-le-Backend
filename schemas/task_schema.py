from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str
    start_date: datetime
    end_date: datetime
    vector: Optional[str] = None  # Champ vector, non obligatoire

    class Config:
        extra = "allow"

class TaskCreate(TaskBase):
    user_ids: List[str]


class TaskOut(TaskBase):
    id: str
    status: str
    user_ids: list[str]

    class Config:
        orm_mode = True
