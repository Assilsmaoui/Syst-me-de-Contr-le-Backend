# Enum pour le statut de tâche
from enum import Enum


class TaskStatus(str, Enum):
    NOT_STARTED = "non commencé"
    IN_PROGRESS = "en cours"
    COMPLETED = "terminé"
    LATE = "en retard"

# Modèle de tâche avec lien vers projet
from pydantic import BaseModel
from typing import Optional

class Task(BaseModel):
    # ... autres champs de la tâche ...
    project_id: str  # ID du projet auquel appartient la tâche
