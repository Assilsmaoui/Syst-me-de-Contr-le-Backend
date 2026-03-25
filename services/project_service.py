async def get_projects_by_user(user_id: str) -> list:
    db = get_db()
    cursor = db["projects"].find({"membres": user_id})
    projects = []
    async for project in cursor:
        project["_id"] = str(project["_id"])
        projects.append(project)
    return projects
async def get_all_projects() -> list:
    db = get_db()
    cursor = db["projects"].find()
    projects = []
    async for project in cursor:
        # Convertir l'_id en string pour la réponse
        project["_id"] = str(project["_id"])
        projects.append(project)
    return projects
from models.project_model import Project
from typing import Any
from fastapi import HTTPException
from database import get_db

async def create_project(project_data: dict) -> Any:
    import datetime
    db = get_db()
    # Conversion des dates en string 'YYYY-MM-DD' si elles existent
    if project_data.get("date_debut") and isinstance(project_data["date_debut"], datetime.date):
        project_data["date_debut"] = project_data["date_debut"].strftime("%Y-%m-%d")
    if project_data.get("date_fin") and isinstance(project_data["date_fin"], datetime.date):
        project_data["date_fin"] = project_data["date_fin"].strftime("%Y-%m-%d")
    project = Project(**project_data)
    doc = project.dict(by_alias=True)
    # Sécurité : forcer la conversion sur le dict final
    if doc.get("date_debut") and isinstance(doc["date_debut"], datetime.date):
        doc["date_debut"] = doc["date_debut"].strftime("%Y-%m-%d")
    if doc.get("date_fin") and isinstance(doc["date_fin"], datetime.date):
        doc["date_fin"] = doc["date_fin"].strftime("%Y-%m-%d")
    # Supprimer _id si None pour laisser MongoDB le générer
    if doc.get("_id") is None:
        doc.pop("_id")
    result = await db["projects"].insert_one(doc)
    if result.inserted_id:
        return str(result.inserted_id)
    raise HTTPException(status_code=500, detail="Erreur lors de la création du projet")
