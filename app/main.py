from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, clients, matters, tasks, billing, documents, time_tracking, events, audit_logs, conflicts, trust, expenses

app = FastAPI(title="LFMS Complete Backed", version="1.0.0")

app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(matters.router)
app.include_router(tasks.router)
app.include_router(billing.router)
app.include_router(documents.router)
app.include_router(time_tracking.router)
app.include_router(events.router)
app.include_router(audit_logs.router)
app.include_router(conflicts.router)
app.include_router(trust.router)
app.include_router(expenses.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Law Firm Management System API  is live and running."}