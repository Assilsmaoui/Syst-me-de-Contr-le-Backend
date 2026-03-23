from fastapi import Header, Request
from fastapi import APIRouter, HTTPException, Depends
from schemas.user_schema import UserCreate, UserLogin, UserOut
from auth.auth_service import create_user, authenticate_user, create_token_for_user
from database import get_db

# Importer la blacklist et le handler JWT
from auth.jwt_blacklist import add_token_to_blacklist
from auth.jwt_handler import verify_access_token


router = APIRouter()


# Endpoint de logout avec JWT (blacklist) et désactivation utilisateur
@router.post("/logout")
async def logout(request: Request, db=Depends(get_db)):
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant ou invalide")
    token = auth_header.split(" ", 1)[1]
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalide")
    # Désactiver l'utilisateur (is_active = False)
    username = payload.get("sub") or payload.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="Impossible de trouver l'utilisateur dans le token")
    result = await db["users"].update_one({"username": username}, {"$set": {"is_active": False}})
    add_token_to_blacklist(token)
    return {"message": "Déconnexion réussie (token invalidé, utilisateur désactivé)", "is_active": False}






@router.post("/register", response_model=UserOut)
async def register(user: UserCreate, db=Depends(get_db)):
    try:
        user_obj = await create_user(user.username, user.password, db, role="user", email=user.email, domaine=user.domaine)
        return {
            "username": user_obj["username"],
            "email": user_obj["email"],
            "domaine": user_obj["domaine"],
            "is_active": user_obj["is_active"],
            "role": user_obj["role"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/create-admin", response_model=UserOut)
async def create_admin(user: UserCreate, db=Depends(get_db)):
    try:
        user_obj = await create_user(user.username, user.password, db, role="admin", email=user.email, domaine=user.domaine)
        return {
            "username": user_obj["username"],
            "email": user_obj["email"],
            "domaine": user_obj["domaine"],
            "is_active": user_obj["is_active"],
            "role": user_obj["role"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login(user: UserLogin, db=Depends(get_db)):
    user_obj = await authenticate_user(user.username, user.password, db)
    if not user_obj:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token_for_user(user_obj)
    return {"access_token": token, "token_type": "bearer"}
