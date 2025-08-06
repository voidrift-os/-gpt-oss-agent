from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class MoodBase(BaseModel):
    mood_level: int  # 1-10 scale
    mood_type: Optional[str] = None
    notes: Optional[str] = None
    date: datetime

    @validator("mood_level")
    def validate_mood_level(cls, value):
        if not 1 <= value <= 10:
            raise ValueError("Mood level must be between 1 and 10")
        return value


class MoodCreate(MoodBase):
    pass


class MoodUpdate(BaseModel):
    mood_level: Optional[int] = None
    mood_type: Optional[str] = None
    notes: Optional[str] = None
    date: Optional[datetime] = None


class MoodInDBBase(MoodBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Mood(MoodInDBBase):
    pass


class MoodInDB(MoodInDBBase):
    pass
