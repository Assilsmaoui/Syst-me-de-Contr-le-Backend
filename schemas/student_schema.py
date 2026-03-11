from pydantic import BaseModel, Field
from typing import List, Optional

class Address(BaseModel):
    city: str
    zip: str

class StudentSchema(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    field: Optional[str] = None
    skills: Optional[List[str]] = None
    address: Optional[Address] = None

class StudentDB(StudentSchema):
    id: str = Field(..., alias="_id")
