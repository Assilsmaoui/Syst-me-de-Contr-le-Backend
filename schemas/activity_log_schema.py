from pydantic import BaseModel

class ActivityLogSchema(BaseModel):
    start: str
    end: str
    app: str
    duration: float
    username: str
