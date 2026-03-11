from database import get_db
from bson import ObjectId

async def get_all_students(db):
    students = await db["students"].find().to_list(100)
    for student in students:
        student["_id"] = str(student["_id"])
    return students
