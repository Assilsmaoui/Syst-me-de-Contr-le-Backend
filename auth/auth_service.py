import bcrypt
import hashlib
from auth.jwt_handler import create_access_token
from datetime import timedelta

def _password_digest(password: str) -> bytes:
    # Accepte toute longueur/caractère de mot de passe sans limite bcrypt des 72 octets.
    return hashlib.sha256(password.encode("utf-8")).digest()

def get_password_hash(password):
    digest = _password_digest(password)
    hashed = bcrypt.hashpw(digest, bcrypt.gensalt()).decode("utf-8")
    return f"sha256${hashed}"

def verify_password(plain_password, hashed_password):
    digest = _password_digest(plain_password)
    try:
        # Nouveau format: sha256$<bcrypt_hash>
        if hashed_password.startswith("sha256$"):
            hash_bytes = hashed_password.split("$", 1)[1].encode("utf-8")
            return bcrypt.checkpw(digest, hash_bytes)

        # Compatibilite anciens comptes deja en base (bcrypt classique)
        raw = plain_password.encode("utf-8")
        if len(raw) > 72:
            raw = raw[:72]
        return bcrypt.checkpw(raw, hashed_password.encode("utf-8"))
    except ValueError:
        return False

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
    # MongoDB stocke l'id sous '_id', qui peut être un ObjectId
    user_id = user.get("_id")
    if user_id is not None:
        user_id = str(user_id)
    else:
        user_id = ""
    return create_access_token({
        "sub": user["username"],
        "role": user["role"],
        "user_id": user_id
    }, expires_delta=timedelta(minutes=30))

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
