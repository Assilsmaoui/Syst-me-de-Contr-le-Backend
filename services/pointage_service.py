from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["university"]
pointage_collection = db["pointage"]

class PointageService:
    @staticmethod
    def enregistrer_pointage(data):
        # Conversion des dates
        start_app = datetime.strptime(data["start_app"], "%Y-%m-%d %H:%M:%S")
        fin_app = datetime.strptime(data["fin_app"], "%Y-%m-%d %H:%M:%S")
        pointage = {
            "user": data["user"],
            "app": data["app"],
            "start_app": start_app,
            "fin_app": fin_app,
            "duree": data["duree"]
        }
        pointage_collection.insert_one(pointage)
        return True
