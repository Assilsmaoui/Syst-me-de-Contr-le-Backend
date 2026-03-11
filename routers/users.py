from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from typing import List

router = APIRouter()

@router.get("/users", response_model=List[dict])
async def list_users(db=Depends(get_db)):
    users = await db["users"].find().to_list(100)
    for user in users:
        user.pop("hashed_password", None)
        if "_id" in user:
            user["_id"] = str(user["_id"])
    return users
