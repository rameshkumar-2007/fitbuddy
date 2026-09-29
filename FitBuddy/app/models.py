from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str]=mapped_column(String(64), unique=True, index=True)
    name: Mapped[str]=mapped_column(String(100))
    age: Mapped[int]=mapped_column(Integer)
    weight: Mapped[float]=mapped_column(Float)
    goal: Mapped[str]=mapped_column(String(50))
    intensity: Mapped[str]=mapped_column(String(20))
    original_plan: Mapped[str]=mapped_column(Text)
    updated_plan: Mapped[str|None]=mapped_column(Text, nullable=True)
    nutrition_tip: Mapped[str]=mapped_column(Text)
    feedback: Mapped[str|None]=mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now(), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now(), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
