from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List
from backend.config.database import get_db
import backend.models.index as models
import backend.schemas.index as schemas
from backend.services.auth import get_current_user
from datetime import date

router = APIRouter(prefix="", tags=["Expenses"])

@router.post("/", response_model=schemas.ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Verify category exists
    category = db.query(models.Category).filter(models.Category.id == expense.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    new_expense = models.Expense(**expense.dict(), user_id=current_user.id)
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense

@router.get("/", response_model=List[schemas.ExpenseResponse])
def get_expenses(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    expenses = db.query(models.Expense).filter(models.Expense.user_id == current_user.id).order_by(models.Expense.date.desc()).all()
    return expenses

@router.put("/{expense_id}", response_model=schemas.ExpenseResponse)
def update_expense(expense_id: int, expense_data: schemas.ExpenseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id, models.Expense.user_id == current_user.id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Verify category
    category = db.query(models.Category).filter(models.Category.id == expense_data.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    for key, value in expense_data.dict().items():
        setattr(expense, key, value)
    
    db.commit()
    db.refresh(expense)
    return expense

@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id, models.Expense.user_id == current_user.id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    db.delete(expense)
    db.commit()
    return None

@router.post("/expenses-form")
def create_expense_form(
    amount: float = Form(...),
    category_id: int = Form(...),
    date: date = Form(...),
    note: str = Form(None),
    source: str = Form("dashboard"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        return RedirectResponse(url="/dashboard?error=Category+not+found", status_code=status.HTTP_303_SEE_OTHER)

    new_expense = models.Expense(amount=amount, category_id=category_id, date=date, note=note, user_id=current_user.id)
    db.add(new_expense)
    db.commit()
    redirect_url = f"/{source}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)

@router.post("/expenses-edit-form/{expense_id}")
def edit_expense_form(
    expense_id: int,
    amount: float = Form(...),
    category_id: int = Form(...),
    date: date = Form(...),
    note: str = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id, models.Expense.user_id == current_user.id).first()
    if not expense:
        return RedirectResponse(url="/entries", status_code=status.HTTP_303_SEE_OTHER)
        
    expense.amount = amount
    expense.category_id = category_id
    expense.date = date
    expense.note = note
    db.commit()
    return RedirectResponse(url="/entries", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/expenses-delete/{expense_id}")
def delete_expense_form(expense_id: int, source: str = Form("dashboard"), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id, models.Expense.user_id == current_user.id).first()
    if expense:
        db.delete(expense)
        db.commit()
    redirect_url = f"/{source}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)

@router.post("/incomes-form")
def create_income_form(
    amount: float = Form(...),
    category_id: int = Form(...),
    date: date = Form(...),
    note: str = Form(None),
    source: str = Form("entries"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        return RedirectResponse(url="/entries?error=Category+not+found", status_code=status.HTTP_303_SEE_OTHER)

    new_income = models.Income(amount=amount, category_id=category_id, date=date, note=note, user_id=current_user.id)
    db.add(new_income)
    db.commit()
    redirect_url = f"/{source}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)

@router.post("/incomes-edit-form/{income_id}")
def edit_income_form(
    income_id: int,
    amount: float = Form(...),
    category_id: int = Form(...),
    date: date = Form(...),
    note: str = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    income = db.query(models.Income).filter(models.Income.id == income_id, models.Income.user_id == current_user.id).first()
    if not income:
        return RedirectResponse(url="/entries", status_code=status.HTTP_303_SEE_OTHER)
        
    income.amount = amount
    income.category_id = category_id
    income.date = date
    income.note = note
    db.commit()
    return RedirectResponse(url="/entries", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/incomes-delete/{income_id}")
def delete_income_form(income_id: int, source: str = Form("entries"), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    income = db.query(models.Income).filter(models.Income.id == income_id, models.Income.user_id == current_user.id).first()
    if income:
        db.delete(income)
        db.commit()
    redirect_url = f"/{source}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)
