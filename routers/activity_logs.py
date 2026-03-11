from fastapi import APIRouter, HTTPException, Query
from schemas.activity_log_schema import ActivityLogSchema
from services.activity_log_service import ActivityLogService, activity_logs_collection
from services.pointage_service import PointageService

router = APIRouter(prefix="/activity_logs", tags=["Activity Logs"])

@router.post("/")
def create_activity_log(log: ActivityLogSchema):
    try:
        ActivityLogService.create_activity_log(log.dict())
        return {"message": "Log enregistré avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint GET pour récupérer les logs
@router.get("/")
def get_activity_logs(limit: int = Query(10, ge=1, le=100)):
    try:
        logs = list(activity_logs_collection.find().sort("start", -1).limit(limit))
        for log in logs:
            log["_id"] = str(log["_id"])
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
