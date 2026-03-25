
import os
from openai import AzureOpenAI
import numpy as np

async def get_tasks_by_project(project_id: str) -> list:
    from database import get_db
    db = get_db()
    cursor = db["tasks"].find({"project_id": project_id})
    tasks = []
    async for task in cursor:
        task["_id"] = str(task["_id"])
        tasks.append(task)
    return tasks

# Fonction pour vectoriser une nouvelle tâche (titre + description)
def vectorize_task(title: str, description: str):
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_API_KEY"),
        api_version="2024-12-01-preview",
        azure_endpoint=os.getenv("AZURE_ENDPOINT")
    )
    text = f"{title} {description}"
    try:
        response = client.embeddings.create(
            input=text,
            model=os.getenv("AZURE_EMBEDDING_MODEL", "text-embedding-ada-002")
        )
        embedding = response.data[0].embedding
        return embedding
    except Exception as e:
        print(f"Erreur vectorisation tâche: {e}")
        return None

# Fonction pour suggérer automatiquement les utilisateurs les plus pertinents pour une tâche


async def suggest_users_for_task(project_id: str, title: str, description: str, top_k: int = 3, threshold: float = 0.5):
    from database import get_db
    db = get_db()
    # Debug désactivé
    # 1. Vectoriser la nouvelle tâche
    task_vector = vectorize_task(title, description)
    if task_vector is None:
        return []
    # 2. Récupérer les utilisateurs du projet
    # Essayer d'abord avec string, puis avec ObjectId si None
    project = await db["projects"].find_one({"_id": project_id})
    if not project:
        try:
            from bson import ObjectId
            project = await db["projects"].find_one({"_id": ObjectId(project_id)})
        except Exception:
            pass
    if not project:
        return []
    user_ids = project.get("users")
    if not user_ids:
        user_ids = project.get("membres", [])
    # Debug désactivé
    # 3. Pour chaque user, calculer un score de similarité avec l'historique de ses tâches
    user_scores = []
    for user_id in user_ids:
        user_tasks = db["tasks"].find({
            "user_ids": user_id,
            "vector": {"$exists": True}
        })
        similarities = []
        count = 0
        async for t in user_tasks:
            count += 1
            vec = t.get("vector")
            if vec:
                sim = np.dot(task_vector, vec) / (np.linalg.norm(task_vector) * np.linalg.norm(vec))
                similarities.append(sim)
        # Debug désactivé
        score = float(np.mean(similarities)) if similarities else 0.0
        user_scores.append((user_id, score))
    # Debug désactivé
    user_scores.sort(key=lambda x: x[1], reverse=True)
    # Appliquer le threshold
    filtered = [u[0] for u in user_scores if u[1] >= threshold]
    # Debug désactivé
    return filtered[:top_k]
    print(f"[DEBUG] Scores finaux: {user_scores}")
    user_scores.sort(key=lambda x: x[1], reverse=True)
    return [u[0] for u in user_scores[:top_k]]

# Fonction pour vectoriser toutes les tâches existantes
async def vectorize_all_tasks():
    from database import get_db
    db = get_db()
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_API_KEY"),
        api_version="2024-12-01-preview",
        azure_endpoint=os.getenv("AZURE_ENDPOINT")
    )
    cursor = db["tasks"].find({})
    async for task in cursor:
        title = task.get("title", "")
        description = task.get("description", "")
        text = f"{title} {description}"
        # Appel à Azure OpenAI pour générer l'embedding
        embedding = None
        try:
            response = client.embeddings.create(
                input=text,
                model=os.getenv("AZURE_EMBEDDING_MODEL", "text-embedding-ada-002")
            )
            embedding = response.data[0].embedding
        except Exception as e:
            print(f"Erreur vectorisation tâche {task.get('_id')}: {e}")
            continue
        # Mettre à jour la tâche avec le champ vector
        await db["tasks"].update_one(
            {"_id": task["_id"]},
            {"$set": {"vector": embedding}}
        )
    return {"message": "Vectorisation terminée"}
