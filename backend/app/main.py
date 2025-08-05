from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import users, groups, sms
from app.db.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Group SMS Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(groups.router, prefix="/api/groups", tags=["groups"])
app.include_router(sms.router, prefix="/api/sms", tags=["sms"])

@app.get("/")
def read_root():
    return {"message": "Group SMS Chat API"}