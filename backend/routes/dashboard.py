from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.config.database import get_db
import backend.models.index as models
from backend.services.auth import get_current_user
from datetime import date, timedelta
import calendar

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def get_dashboard_data(db: Session, current_user: models.User, month: int = None, year: int = None):
    today = date.today()
    if not year:
        year = today.year
    if not month:
        month = today.month
        
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    
    total_expense = db.query(func.sum(models.Expense.amount)).filter(models.Expense.user_id == current_user.id).scalar() or 0.0
    this_month_expense = db.query(func.sum(models.Expense.amount)).filter(
        models.Expense.user_id == current_user.id,
        models.Expense.date >= start_date,
        models.Expense.date <= end_date
    ).scalar() or 0.0

    total_income_sum = db.query(func.sum(models.Income.amount)).filter(models.Income.user_id == current_user.id).scalar() or 0.0
    total_balance = total_income_sum - total_expense

    # Daily (Selected Month)
    daily_expenses_query = db.query(
        models.Expense.date,
        func.sum(models.Expense.amount).label("total")
    ).filter(
        models.Expense.user_id == current_user.id,
        models.Expense.date >= start_date,
        models.Expense.date <= end_date
    ).group_by(models.Expense.date).order_by(models.Expense.date).all()
    
    daily_expenses = [{"date": str(e.date), "amount": e.total} for e in daily_expenses_query]

    # Monthly (Global Bar Graph)
    monthly_expenses_query = db.query(
        func.strftime("%m", models.Expense.date).label("month"),
        func.sum(models.Expense.amount).label("total")
    ).filter(
        models.Expense.user_id == current_user.id,
        func.strftime("%Y", models.Expense.date) == str(year)
    ).group_by("month").order_by("month").all()
    
    monthly_expenses = [{"month": int(e.month), "amount": e.total} for e in monthly_expenses_query]

    # Categories Breakdown
    cat_distribution = db.query(
        models.Category.name,
        func.sum(models.Expense.amount).label("total")
    ).join(models.Expense, models.Category.id == models.Expense.category_id).filter(
        models.Expense.user_id == current_user.id,
        models.Expense.date >= start_date,
        models.Expense.date <= end_date
    ).group_by(models.Category.name).all()

    cat_distribution_json = [{"name": c.name, "amount": c.total} for c in cat_distribution]

    # Recent Expenses
    recent_expenses = db.query(models.Expense).filter(
        models.Expense.user_id == current_user.id
    ).order_by(models.Expense.date.desc()).limit(10).all()

    # All Categories (for form)
    categories = db.query(models.Category).filter(
        (models.Category.created_by_id == current_user.id) | 
        (models.Category.created_by_id.is_(None))
    ).all()

    return {
        "total_expense": total_expense,
        "this_month_expense": this_month_expense,
        "total_balance": total_balance,
        "total_income": total_income_sum,
        "daily_expenses": daily_expenses,
        "monthly_expenses": monthly_expenses,
        "cat_distribution": cat_distribution_json,
        "user": current_user,
        "selected_month": month,
        "selected_year": year
    }



@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    today = date.today()
    current_month_start = today.replace(day=1)
    
    # Total Expenses (All time)
    total_expense = db.query(func.sum(models.Expense.amount)).filter(models.Expense.user_id == current_user.id).scalar() or 0.0
    
    # This month expense
    this_month_expense = db.query(func.sum(models.Expense.amount)).filter(
        models.Expense.user_id == current_user.id,
        models.Expense.date >= current_month_start
    ).scalar() or 0.0

    return {
        "total_expense": total_expense,
        "this_month_expense": this_month_expense,
        "savings": 0 # Future implement total income vs expense
    }

@router.get("/daily")
def get_daily_expenses(month: int = None, year: int = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not month or not year:
        today = date.today()
        month = today.month
        year = today.year
        
    start_date = date(year, month, 1)
    # get last day of month
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    expenses = db.query(
        models.Expense.date,
        func.sum(models.Expense.amount).label("total")
    ).filter(
        models.Expense.user_id == current_user.id,
        models.Expense.date >= start_date,
        models.Expense.date <= end_date
    ).group_by(models.Expense.date).order_by(models.Expense.date).all()

    return [{"date": str(e.date), "amount": e.total} for e in expenses]

@router.get("/monthly")
def get_monthly_summary(year: int = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not year:
        year = date.today().year

    # Basic SQLite extraction for month, depends on dialect for true SQL cross-compatibility
    # For simplicity and standard SQL, we process in memory or use cast. 
    # SQLAlchemy func.extract('month', date) works across major dialects.
    
    expenses_query = db.query(
        func.strftime("%m", models.Expense.date).label("month"),
        func.sum(models.Expense.amount).label("total")
    ).filter(
        models.Expense.user_id == current_user.id,
        func.strftime("%Y", models.Expense.date) == str(year)
    ).group_by("month").order_by("month").all()

    return [{"month": e.month, "amount": e.total} for e in expenses_query]

@router.get("/category-distribution")
def get_category_distribution(month: int = None, year: int = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    query = db.query(
        models.Category.name,
        func.sum(models.Expense.amount).label("total")
    ).join(models.Expense, models.Category.id == models.Expense.category_id).filter(
        models.Expense.user_id == current_user.id
    )

    if month and year:
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
        query = query.filter(models.Expense.date >= start_date, models.Expense.date <= end_date)

    distribution = query.group_by(models.Category.name).all()

    return [{"category": d.name, "amount": d.total} for d in distribution]
