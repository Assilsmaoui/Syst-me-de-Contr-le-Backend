from fastapi import APIRouter, Depends
from database import get_db
from schemas.student_schema import StudentDB
from services.student_service import get_all_students
from typing import List

router = APIRouter()

@router.get("/students", response_model=List[StudentDB])
async def get_students(db=Depends(get_db)):
    return await get_all_students(db)
