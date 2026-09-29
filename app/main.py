from fastapi import FastAPI
from app.database import engine, Base

app = FastAPI(title="LFMS Complete Backed", version="1.0.0")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Law Firm Management System API  is live and running."}