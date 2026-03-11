from fastapi import APIRouter, HTTPException, Body
from services.pointage_service import PointageService

router = APIRouter(prefix="/pointage", tags=["Pointage"])

@router.post("/")
def enregistrer_pointage(data: dict = Body(...)):
    try:
        PointageService.enregistrer_pointage(data)
        return {"message": "Pointage enregistré avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
