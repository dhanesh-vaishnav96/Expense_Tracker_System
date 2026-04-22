from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional, List

# --- User Schemas ---
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Category Schemas ---
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    created_by_id: Optional[int] = None

    class Config:
        from_attributes = True

# --- Expense Schemas ---
class ExpenseBase(BaseModel):
    amount: float
    date: date
    note: Optional[str] = None
    category_id: int

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    id: int
    user_id: int
    created_at: datetime
    category: CategoryResponse

    class Config:
        from_attributes = True

# --- Income Schemas ---
class IncomeBase(BaseModel):
    amount: float
    date: date
    note: Optional[str] = None
    category_id: int

class IncomeCreate(IncomeBase):
    pass

class IncomeResponse(IncomeBase):
    id: int
    user_id: int
    created_at: datetime
    category: CategoryResponse

    class Config:
        from_attributes = True

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
