from pydantic import BaseModel
from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TimestampMixin:
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ✅ Pydantic BaseSchema
class BaseSchema(BaseModel):
    class Config:
        orm_mode = True
