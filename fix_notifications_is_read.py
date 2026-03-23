# Script pour corriger les notifications existantes dans MongoDB
# Ajoute le champ is_read: False si absent

from pymongo import MongoClient

MONGO_DETAILS = "mongodb://localhost:27017"
client = MongoClient(MONGO_DETAILS)
db = client["university"]

result = db["notifications"].update_many(
    {"is_read": {"$exists": False}},
    {"$set": {"is_read": False}}
)

print(f"Notifications corrigées : {result.modified_count}")
