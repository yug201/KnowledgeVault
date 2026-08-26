from contextlib import asynccontextmanager
from app.routes import auth, knowledge, todos, files
from fastapi import FastAPI
from app.db.database import Base, engine
from app.db import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield


app=FastAPI(
    title="Personal Knowledge Vault",
    lifespan=lifespan
)
app.include_router(auth.router)
app.include_router(knowledge.router)
app.include_router(todos.router)
app.include_router(files.router)
@app.get("/")
async def root():
    return {"message": "Personal Knowledge Vault API is running"}