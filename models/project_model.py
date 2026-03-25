from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date

class Project(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    nom_projet: str
    description: Optional[str] = None
    statut: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    membres: List[str] = []  # Liste des IDs des membres
