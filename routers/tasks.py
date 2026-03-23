from fastapi import APIRouter, HTTPException, Depends
from schemas.task_schema import TaskCreate, TaskOut
from schemas.notification_schema import NotificationCreate
from models.task_model import TaskStatus
from database import get_db
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from datetime import datetime
from routers.notifications_ws import send_notification_to_user

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)



@router.post("/", response_model=TaskOut)
async def create_task(task: TaskCreate, db=Depends(get_db)):
    task_dict = jsonable_encoder(task)
    # Toujours convertir user_ids en liste de str
    task_dict["user_ids"] = [str(uid) for uid in task.user_ids]
    task_dict["status"] = TaskStatus.NOT_STARTED
    result = await db["tasks"].insert_one(task_dict)
    task_dict["id"] = str(result.inserted_id)
    # Nettoyage pour la réponse : convertir tout ObjectId en str
    if "user_ids" in task_dict:
        task_dict["user_ids"] = [str(uid) for uid in task_dict["user_ids"]]
    for k, v in list(task_dict.items()):
        try:
            from bson import ObjectId
            if isinstance(v, ObjectId):
                task_dict[k] = str(v)
        except ImportError:
            pass
    # Créer une notification pour chaque utilisateur
    for user_id in task.user_ids:
        notif = NotificationCreate(
            user_id=str(user_id),
            message=f"Nouvelle tâche assignée : {task.title}"
        )
        notif_dict = jsonable_encoder(notif)
        await db["notifications"].insert_one(notif_dict)
        # Envoi temps réel via WebSocket
        await send_notification_to_user(str(user_id), notif.message)
    return TaskOut(**task_dict)

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
