from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.users import router as user_router
from app.routers.jobs import router as job_router
from app.routers.resumes import router as resume_router
from app.routers.aplications import router as aplication_router
from app.routers.auth import router as auth_router
from app.routers.messages import router as messages_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(job_router)
app.include_router(resume_router)
app.include_router(aplication_router)
app.include_router(auth_router)
app.include_router(messages_router)
