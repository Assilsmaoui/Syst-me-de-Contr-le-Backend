from pydantic import BaseModel



class UserCreate(BaseModel):
    username: str
    email: str
    domaine: str
    password: str


class UserLogin(BaseModel):
    username: str
    email: str = None  # Optionnel pour compatibilité, mais non utilisé pour login
    password: str



class UserOut(BaseModel):
    username: str
    email: str
    domaine: str
    is_active: bool
    role: str
