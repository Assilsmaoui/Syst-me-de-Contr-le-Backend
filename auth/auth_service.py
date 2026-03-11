from passlib.context import CryptContext
from auth.jwt_handler import create_access_token, verify_access_token
from datetime import timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def truncate_password(password: str) -> str:
    b = password.encode("utf-8")
    if len(b) <= 72:
        return password
    truncated = b[:72]
    while True:
        try:
            return truncated.decode("utf-8")
        except UnicodeDecodeError:
            truncated = truncated[:-1]

def get_password_hash(password):
    return pwd_context.hash(truncate_password(password))

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(truncate_password(plain_password), hashed_password)

# --- MongoDB ---


async def create_user(username: str, password: str, db, role: str = "user", email: str = None, domaine: str = None):
    hashed_password = get_password_hash(password)
    user = {
        "username": username,
        "email": email,
        "domaine": domaine,
        "hashed_password": hashed_password,
        "is_active": False,  # Inactif par défaut
        "role": role
    }
    result = await db["users"].insert_one(user)
    print(f"MongoDB insert result: inserted_id={result.inserted_id}")
    return user

def create_token_for_user(user):
    return create_access_token({"sub": user["username"], "role": user["role"]}, expires_delta=timedelta(minutes=30))

async def authenticate_user(username: str, password: str, db):
    user = await db["users"].find_one({"username": username})
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    # Mettre à jour is_active à True lors de la connexion
    await db["users"].update_one({"username": username}, {"$set": {"is_active": True}})
    user["is_active"] = True
    return user
