from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str
    domaine: str
    hashed_password: str
    is_active: bool = True
