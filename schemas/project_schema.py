from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date

class ProjectCreateSchema(BaseModel):
    nom_projet: str
    description: Optional[str] = None
    statut: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    membres: List[str] = []

class ProjectSchema(ProjectCreateSchema):
    id: Optional[str] = Field(alias="_id")
