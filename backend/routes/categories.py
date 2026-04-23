from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List
from backend.config.database import get_db
import backend.models.index as models
import backend.schemas.index as schemas
from backend.services.auth import get_current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("/", response_model=List[schemas.CategoryResponse])
def get_categories(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Return categories created by this user or system defaults
    categories = db.query(models.Category).filter(
        (models.Category.created_by_id == current_user.id) | (models.Category.created_by_id.is_(None))
    ).all()
    return categories

@router.post("/", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Check if category already exists for this user or as a system default
    db_category = db.query(models.Category).filter(
        func.lower(models.Category.name) == func.lower(category.name.strip()),
        models.Category.type == category.type,
        (models.Category.created_by_id == current_user.id) | (models.Category.created_by_id.is_(None))
    ).first()
    if db_category:
        raise HTTPException(status_code=400, detail="Category already exists in your list")
    
    new_category = models.Category(name=category.name.strip(), type=category.type, created_by_id=current_user.id)
    db.add(new_category)
    try:
        db.commit()
        db.refresh(new_category)
        return new_category
    except IntegrityError:
        db.rollback()
        # This might still happen if there's another constraint we missed, but we've dropped the unique index
        raise HTTPException(status_code=400, detail="Category already exists")

@router.put("/{category_id}", response_model=schemas.CategoryResponse)
def update_category(category_id: int, category: schemas.CategoryCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
        
    if db_category.created_by_id is None:
        raise HTTPException(status_code=403, detail="System default categories cannot be modified.")
        
    if db_category.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this category.")
        
    db_category.name = category.name
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
        
    if category.created_by_id is None:
        raise HTTPException(status_code=403, detail="System default categories cannot be deleted.")

    if category.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this category.")
    
    expenses_using = db.query(models.Expense).filter(models.Expense.category_id == category_id).count()
    incomes_using = db.query(models.Income).filter(models.Income.category_id == category_id).count()
    if expenses_using > 0 or incomes_using > 0:
        raise HTTPException(status_code=400, detail="Cannot delete category because it is being used by existing transactions.")

    db.delete(category)
    db.commit()
    return None
