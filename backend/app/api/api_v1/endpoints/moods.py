from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.dependencies import get_current_active_user, get_db, rate_limit_general
from app.schemas.user import User
from app.db.models.mood import Mood
from app.schemas.mood import Mood as MoodSchema, MoodCreate, MoodUpdate

router = APIRouter()



@router.get("/", response_model=List[MoodSchema])
async def read_moods(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    _: Any = Depends(rate_limit_general)
) -> Any:
    """Retrieve moods for current user"""
    result = await db.execute(
        select(Mood)
        .where(Mood.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(Mood.date.desc())
    )
    moods = result.scalars().all()
    return [MoodSchema.from_orm(m) for m in moods]



@router.post("/", response_model=MoodSchema)
async def create_mood(
    *,
    db: AsyncSession = Depends(get_db),
    mood_in: MoodCreate,
    current_user: User = Depends(get_current_active_user),
    _: Any = Depends(rate_limit_general)
) -> Any:
    """Create new mood entry"""
    mood = Mood(**mood_in.dict(), owner_id=current_user.id)
    db.add(mood)
    await db.commit()
    await db.refresh(mood)
    return MoodSchema.from_orm(mood)


@router.put("/{mood_id}", response_model=MoodSchema)
async def update_mood(
    *,
    db: AsyncSession = Depends(get_db),
    mood_id: int,
    mood_in: MoodUpdate,
    current_user: User = Depends(get_current_active_user),
    _: Any = Depends(rate_limit_general)
) -> Any:
    """Update a mood entry"""
    result = await db.execute(
        select(Mood).where(
            Mood.id == mood_id,
            Mood.owner_id == current_user.id
        )
    )
    mood = result.scalar_one_or_none()
    
    if not mood:
        raise HTTPException(status_code=404, detail="Mood entry not found")
    
    update_data = mood_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(mood, field, value)
    
    await db.commit()
    await db.refresh(mood)
    return mood


@router.delete("/{mood_id}")
async def delete_mood(
    *,
    db: AsyncSession = Depends(get_db),
    mood_id: int,
    current_user: User = Depends(get_current_active_user),
    _: Any = Depends(rate_limit_general)
) -> Any:
    """Delete a mood entry"""
    result = await db.execute(
        select(Mood).where(
            Mood.id == mood_id,
            Mood.owner_id == current_user.id
        )
    )
    mood = result.scalar_one_or_none()
    
    if not mood:
        raise HTTPException(status_code=404, detail="Mood entry not found")
    
    await db.delete(mood)
    await db.commit()
    return {"message": "Mood entry deleted successfully"}
