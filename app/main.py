# app/main.py
from fastapi import FastAPI

from app.database import Base, engine
from app.routers import admin, public

app = FastAPI()
app.openapi_schema = None
Base.metadata.create_all(bind=engine)

app.include_router(public.router)
app.include_router(admin.router)
