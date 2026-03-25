from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware

from fastapi import Depends


from routers import students
from routers import auth
from routers import users
from routers import activity_logs
from routers import pointage
from routers import tasks
from routers import notifications_ws
from routers import send_notification
from routers import projects


app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Autorise seulement Angular en local
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
 # Inclusion du router projects
app.include_router(projects.router)
 # Inclusion du router pointage
app.include_router(pointage.router)
# Inclusion du router tasks
app.include_router(tasks.router)
# Inclusion du router WebSocket
app.include_router(notifications_ws.router)
app.include_router(send_notification.router)