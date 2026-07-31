from fastapi import FastAPI
from app.routes.upload import router as upload_router

from app.database.database import Base, engine
from app.models.claim import Claim
from app.models.users import User

from app.routes.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(auth_router)

@app.get("/")
def home():
    return {
        "message": "Insurance AI Backend Running Successfully!"
    }