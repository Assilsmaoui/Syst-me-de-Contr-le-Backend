from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends, HTTPException
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from database import get_db
from schemas.notification_schema import NotificationCreate
from datetime import datetime
from typing import Dict, List
from collections import defaultdict

router = APIRouter()

# Marquer une notification individuelle comme lue
@router.put("/notifications/mark_read/{notification_id}")
async def mark_notification_read(notification_id: str, db=Depends(get_db)):
    result = await db["notifications"].update_one(
        {"_id": ObjectId(notification_id)},
        {"$set": {"is_read": True}}
    )
    return {"updated": result.modified_count}

# Stocke les connexions WebSocket par user_id
active_connections: Dict[str, List[WebSocket]] = defaultdict(list)


@router.websocket("/ws/notifications/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    print(f"WebSocket connecté pour user_id: {user_id}")
    await websocket.accept()
    active_connections[user_id].append(websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            print(f"Message reçu sur WebSocket: {msg}")
    except WebSocketDisconnect:
        print(f"WebSocket déconnecté pour user_id: {user_id}")
        active_connections[user_id].remove(websocket)


# Fonction utilitaire pour envoyer une notification à un utilisateur (en temps réel)
import json
from database import get_db
from datetime import datetime


async def send_notification_to_user(user_id: str, message: str):
    db = get_db()
    notif = await db["notifications"].find_one({"user_id": user_id}, sort=[("created_at", -1)])
    if notif:
        notif["id"] = str(notif.get("_id", ""))
        notif.pop("_id", None)
        if "created_at" in notif and isinstance(notif["created_at"], datetime):
            notif["created_at"] = notif["created_at"].isoformat()
        notif_json = json.dumps(notif)
    else:
        notif_json = json.dumps({"message": message})
    print(f"Envoi notification temps réel à user_id: {user_id} -> {notif_json}")
    for ws in active_connections.get(user_id, []):
        try:
            await ws.send_text(notif_json)
        except Exception as e:
            print(f"Erreur envoi WebSocket: {e}")


# Route pour récupérer l'historique des notifications d'un utilisateur

from schemas.notification_schema import NotificationOut
from fastapi import Body

# Récupérer toutes les notifications d'un utilisateur
@router.get("/notifications/{user_id}", response_model=list[NotificationOut])
async def get_notifications_by_user(user_id: str, db=Depends(get_db)):
    notifications_cursor = db["notifications"].find({"user_id": user_id}).sort("created_at", -1)
    notifications = []
    async for notif in notifications_cursor:
        notif["id"] = str(notif.get("_id", ""))
        notif.pop("_id", None)
        if "created_at" in notif and isinstance(notif["created_at"], datetime):
            notif["created_at"] = notif["created_at"].isoformat()
        notifications.append(NotificationOut(**notif))
    return notifications

# Compter les notifications non lues pour un utilisateur
@router.get("/notifications/unread_count/{user_id}")
async def get_unread_notifications_count(user_id: str, db=Depends(get_db)):
    count = await db["notifications"].count_documents({"user_id": user_id, "is_read": False})
    return {"unread_count": count}

# Marquer toutes les notifications comme lues pour un utilisateur
@router.put("/notifications/mark_all_read/{user_id}")
async def mark_all_notifications_read(user_id: str, db=Depends(get_db)):
    result = await db["notifications"].update_many({"user_id": user_id, "is_read": False}, {"$set": {"is_read": True}})
    return {"updated": result.modified_count}
