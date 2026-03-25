
from fastapi import APIRouter, HTTPException, Depends
from schemas.project_schema import ProjectCreateSchema, ProjectSchema
from services.project_service import create_project, get_all_projects, get_projects_by_user
from database import get_db
from bson import ObjectId
from typing import List

router = APIRouter(prefix="/projects", tags=["projects"])

# Retourner uniquement les IDs des membres d'un projet
@router.get("/{project_id}/members_ids", response_model=List[str])
async def get_project_members_ids(project_id: str, db=Depends(get_db)):
    project = await db["projects"].find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    membres_ids = project.get("membres", [])
    return membres_ids

# Afficher les membres d'un projet
@router.get("/{project_id}/members", response_model=List[dict])
async def get_project_members(project_id: str, db=Depends(get_db)):
    project = await db["projects"].find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    membres_ids = project.get("membres", [])
    if not membres_ids:
        return []
    users = await db["users"].find({"_id": {"$in": [ObjectId(uid) for uid in membres_ids]}}).to_list(length=100)
    for user in users:
        user["_id"] = str(user["_id"])
        user.pop("hashed_password", None)
    return users

@router.get("/user/{user_id}", response_model=list)
async def get_projects_by_user_route(user_id: str):
    return await get_projects_by_user(user_id)

@router.get("/", response_model=list)
async def list_projects():
    return await get_all_projects()

@router.post("/", status_code=201)
async def add_project(project: ProjectCreateSchema):
    project_id = await create_project(project.dict())
    if not project_id:
        raise HTTPException(status_code=500, detail="Erreur lors de la création du projet")
    return {"project_id": project_id, "message": "Projet créé avec succès"}

# Afficher un projet par son id
@router.get("/{project_id}", response_model=ProjectSchema)
async def get_project_by_id(project_id: str, db=Depends(get_db)):
    project = await db["projects"].find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    project["_id"] = str(project["_id"])
    return project

# Modifier un projet
@router.put("/{project_id}", response_model=ProjectSchema)
async def update_project(project_id: str, project: ProjectCreateSchema, db=Depends(get_db)):
    result = await db["projects"].update_one(
        {"_id": ObjectId(project_id)},
        {"$set": project.dict(exclude_unset=True)}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    updated = await db["projects"].find_one({"_id": ObjectId(project_id)})
    updated["_id"] = str(updated["_id"])
    return updated

# Supprimer un projet
@router.delete("/{project_id}")
async def delete_project(project_id: str, db=Depends(get_db)):
    result = await db["projects"].delete_one({"_id": ObjectId(project_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    return {"message": "Projet supprimé avec succès"}
