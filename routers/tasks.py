# ========== SCHÉMA POUR AUTO CRÉATION =============
from pydantic import BaseModel
from typing import Optional

from typing import List



# Ajouter une tâche à un projet via l'URL

# ================= IMPORTS =================
from fastapi import APIRouter, HTTPException, Depends, Body


# ================= ROUTER =================
from schemas.task_schema import TaskCreate, TaskOut
from schemas.notification_schema import NotificationCreate
from models.task_model import TaskStatus
from database import get_db
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from datetime import datetime
from routers.notifications_ws import send_notification_to_user
from services.task_service import get_tasks_by_project, suggest_users_for_task, vectorize_all_tasks

router = APIRouter(prefix="/tasks", tags=["tasks"])


# Endpoint pour créer une tâche avec vectorisation automatique et affectation automatique des users
@router.post("/auto_create/{project_id}")
async def auto_create_task(
    project_id: str,
    task: TaskCreate = Body(...),
    db=Depends(get_db)
):
    """
    Crée une tâche avec vectorisation automatique et affectation automatique des users selon la similarité historique.
    Tous les champs sont acceptés, mais user_ids, vector, project_id sont ignorés côté backend (remplis automatiquement).
    """
    from services.task_service import vectorize_task, suggest_users_for_task
    # 1. Vectorisation automatique
    vector = vectorize_task(task.title, task.description)
    # 2. Affectation automatique des users
    user_ids = await suggest_users_for_task(project_id, task.title, task.description)
    # 3. Création de la tâche
    task_dict = {
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "start_date": task.start_date,
        "end_date": task.end_date,
        "vector": vector,
        "user_ids": user_ids,
        "project_id": project_id
    }
    result = await db["tasks"].insert_one(task_dict)
    task_dict["id"] = str(result.inserted_id)
    # Convertir tous les ObjectId en str pour la réponse
    for k, v in list(task_dict.items()):
        try:
            from bson import ObjectId
            if isinstance(v, ObjectId):
                task_dict[k] = str(v)
        except ImportError:
            pass
    return task_dict



# ================= ENDPOINTS ===============

# Endpoint pour vectoriser toutes les tâches existantes
@router.post("/vectorize_all")
async def vectorize_all_tasks_endpoint():
    return await vectorize_all_tasks()

# Ajouter une tâche à un projet via l'URL
@router.post("/project/{project_id}", response_model=TaskOut)
async def create_task_for_project(project_id: str, task: TaskCreate = Body(...), db=Depends(get_db)):
    task_dict = task.dict()
    task_dict["project_id"] = project_id
    task_dict = jsonable_encoder(task_dict)
    task_dict["user_ids"] = [str(uid) for uid in task_dict["user_ids"]]
    task_dict["status"] = TaskStatus.NOT_STARTED
    result = await db["tasks"].insert_one(task_dict)
    task_dict["id"] = str(result.inserted_id)
    if "user_ids" in task_dict:
        task_dict["user_ids"] = [str(uid) for uid in task_dict["user_ids"]]
    for k, v in list(task_dict.items()):
        try:
            if isinstance(v, ObjectId):
                task_dict[k] = str(v)
        except ImportError:
            pass
    for user_id in task.user_ids:
        notif = NotificationCreate(
            user_id=str(user_id),
            message=f"Nouvelle tâche assignée : {task.title}"
        )
        notif_dict = jsonable_encoder(notif)
        await db["notifications"].insert_one(notif_dict)
        await send_notification_to_user(str(user_id), notif.message)
    return TaskOut(**task_dict)




# Endpoint pour lister les tâches d'un projet

@router.post("/auto_create/{project_id}")
async def auto_create_task(
    project_id: str,
    task: TaskCreate = Body(...),
    db=Depends(get_db)
):
    """
    Crée une tâche avec vectorisation automatique et affectation automatique des users selon la similarité historique.
    """
    from services.task_service import vectorize_task, suggest_users_for_task
    # 1. Vectorisation automatique
    vector = vectorize_task(task.title, task.description)
    # 2. Affectation automatique des users
    user_ids = await suggest_users_for_task(project_id, task.title, task.description)
    # 3. Création de la tâche
    task_dict = {
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "start_date": task.start_date,
        "end_date": task.end_date,
        "vector": vector,
        "user_ids": user_ids,
        "project_id": project_id
    }
    result = await db["tasks"].insert_one(task_dict)
    task_dict["id"] = str(result.inserted_id)
    return task_dict

# Endpoint pour afficher toutes les tâches
@router.get("/", response_model=list[TaskOut])
async def get_all_tasks(db=Depends(get_db)):
    tasks_cursor = db["tasks"].find()
    tasks = []
    async for task in tasks_cursor:
        task["id"] = str(task["_id"])
        task.pop("_id", None)
        # S'assurer que user_ids est une liste de str, ou [] si absent
        if "user_ids" in task:
            # Certains documents peuvent contenir des ObjectId dans user_ids
            task["user_ids"] = [str(uid) for uid in task["user_ids"]]
        else:
            task["user_ids"] = []
        # Nettoyer tous les champs qui pourraient être des ObjectId
        for k, v in list(task.items()):
            # Si la valeur est un ObjectId, la convertir en str
            try:
                from bson import ObjectId
                if isinstance(v, ObjectId):
                    task[k] = str(v)
            except ImportError:
                pass
        tasks.append(TaskOut(**task))
    return tasks

# Endpoint pour mettre à jour le statut d'une tâche
from fastapi import Body

@router.put("/{task_id}/status")
async def update_task_status(task_id: str, new_status: str = Body(..., embed=True), db=Depends(get_db)):
    # Chercher la tâche par son ID
    task = await db["tasks"].find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # Vérifier que le statut est valide
    if new_status not in [TaskStatus.NOT_STARTED, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED, TaskStatus.LATE]:
        raise HTTPException(status_code=400, detail="Invalid status")

    # Vérifier si la tâche est en retard
    now = datetime.now()  # naive datetime
    end_date = task.get("end_date")
    if isinstance(end_date, str):
        try:
            end_date = datetime.fromisoformat(end_date)
            if end_date.tzinfo is not None:
                end_date = end_date.replace(tzinfo=None)
        except Exception:
            pass
    # Si la tâche n'est pas terminée et la date actuelle > end_date, statut = en retard
    if new_status != TaskStatus.COMPLETED and end_date and now > end_date:
        new_status = TaskStatus.LATE

    # Mettre à jour le statut
    await db["tasks"].update_one({"_id": ObjectId(task_id)}, {"$set": {"status": new_status}})
    return {"message": "Status updated", "status": new_status}

# Endpoint pour afficher les tâches d'un utilisateur spécifique
@router.get("/user/{user_id}", response_model=list[TaskOut])
async def get_tasks_by_user(user_id: str, db=Depends(get_db)):
    tasks_cursor = db["tasks"].find({"user_ids": user_id})
    tasks = []
    async for task in tasks_cursor:
        task["id"] = str(task["_id"])
        task.pop("_id", None)
        if "user_ids" in task:
            task["user_ids"] = [str(uid) for uid in task["user_ids"]]
        else:
            task["user_ids"] = []
        for k, v in list(task.items()):
            try:
                from bson import ObjectId
                if isinstance(v, ObjectId):
                    task[k] = str(v)
            except ImportError:
                pass
        tasks.append(TaskOut(**task))
    return tasks
