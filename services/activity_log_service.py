from datetime import datetime
from pymongo import MongoClient


# Connexion MongoDB sur la base 'university'
client = MongoClient("mongodb://localhost:27017/")
db = client["university"]
activity_logs_collection = db["activity_logs"]
# Création d'un index unique sur start et end (exécuté une seule fois)
try:
    activity_logs_collection.create_index([("start", 1), ("end", 1)], unique=True)
except Exception:
    pass

class ActivityLogService:
    @staticmethod
    def create_activity_log(data):
        # Conversion des dates
        start = datetime.strptime(data["start"], "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(data["end"], "%Y-%m-%d %H:%M:%S")
        # Vérification d'unicité uniquement sur start et end
        duplicate = activity_logs_collection.find_one({
            "start": start,
            "end": end
        })
        if duplicate:
            raise Exception("Log déjà existant pour ce start et end.")
        log = {
            "start": start,
            "end": end,
            "app": data["app"],
            "duration": data["duration"],
            "username": data["username"]
        }
        activity_logs_collection.insert_one(log)
        return True
