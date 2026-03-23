from fastapi import APIRouter, Depends
from database import get_db
from routers.notifications_ws import send_notification_to_user

router = APIRouter(
    prefix="/test-notif",
    tags=["test-notif"]
)

@router.post("/{user_id}")
async def send_test_notification(user_id: str, db=Depends(get_db)):
    message = "Notification test envoyée en temps réel !"
    await send_notification_to_user(user_id, message)
    return {"status": "Notification envoyée", "user_id": user_id, "message": message}
