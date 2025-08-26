from fastapi import FastAPI
from app.routers.users import router as user_router
from app.routers.jobs import router as job_router
from app.routers.resumes import router as resume_router
from app.routers.aplications import router as aplication_router
from app.routers.auth import router as auth_router


app = FastAPI()

app.include_router(user_router)
app.include_router(job_router)
app.include_router(resume_router)
app.include_router(aplication_router)
app.include_router(auth_router)

