
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi import Depends


from routers import students
from routers import auth
from routers import users
from routers import activity_logs
from routers import pointage


app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Remplace * par l'URL de ton frontend en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return {"message": "API FastAPI fonctionne"}


# Inclusion du router students
app.include_router(students.router)
# Inclusion du router auth
app.include_router(auth.router)
# Inclusion du router users
app.include_router(users.router)
 # Inclusion du router activity_logs
app.include_router(activity_logs.router)
 # Inclusion du router pointage
app.include_router(pointage.router)