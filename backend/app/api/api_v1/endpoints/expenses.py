from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.dependencies import get_current_active_user, get_db, rate_limit_general
from app.schemas.user import User
from app.db.models.expense import Expense
from app.schemas.expense import Expense as ExpenseSchema, ExpenseCreate, ExpenseUpdate

router = APIRouter()



@router.get("/", response_model=List[ExpenseSchema])
async def read_expenses(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    _: Any = Depends(rate_limit_general)
) -> Any:
    """Retrieve expenses for current user"""
    result = await db.execute(
        select(Expense)
        .where(Expense.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(Expense.date.desc())
    )
    expenses = result.scalars().all()
    return [ExpenseSchema.model_validate(e) for e in expenses]



@router.post("/", response_model=ExpenseSchema)
async def create_expense(
    *,
    db: AsyncSession = Depends(get_db),
    expense_in: ExpenseCreate,
    current_user: User = Depends(get_current_active_user),
    _: Any = Depends(rate_limit_general)
) -> Any:
    """Create new expense"""
    expense = Expense(**expense_in.model_dump(), owner_id=current_user.id)
    db.add(expense)
    await db.commit()
    await db.refresh(expense)
    return ExpenseSchema.model_validate(expense)


@router.put("/{expense_id}", response_model=ExpenseSchema)
async def update_expense(
    *,
    db: AsyncSession = Depends(get_db),
    expense_id: int,
    expense_in: ExpenseUpdate,
    current_user: User = Depends(get_current_active_user),
    _: Any = Depends(rate_limit_general)
) -> Any:
    """Update an expense"""
    result = await db.execute(
        select(Expense).where(
            Expense.id == expense_id,
            Expense.owner_id == current_user.id
        )
    )
    expense = result.scalar_one_or_none()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    update_data = expense_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(expense, field, value)
    
    await db.commit()
    await db.refresh(expense)
    return ExpenseSchema.model_validate(expense)


@router.delete("/{expense_id}")
async def delete_expense(
    *,
    db: AsyncSession = Depends(get_db),
    expense_id: int,
    current_user: User = Depends(get_current_active_user),
    _: Any = Depends(rate_limit_general)
) -> Any:
    """Delete an expense"""
    result = await db.execute(
        select(Expense).where(
            Expense.id == expense_id,
            Expense.owner_id == current_user.id
        )
    )
    expense = result.scalar_one_or_none()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    await db.delete(expense)
    await db.commit()
    return {"message": "Expense deleted successfully"}
