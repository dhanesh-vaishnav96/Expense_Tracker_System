import json
import calendar
from datetime import date
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from fastapi import FastAPI, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from backend.config.database import engine, Base, get_db
from backend.routes import auth, expenses, categories, dashboard
from backend.routes.dashboard import get_dashboard_data
from backend.services.auth import get_current_user
from backend.models.index import Expense, Category, Income

# Create tables if not using migrations
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker API", description="Antigravity Expense Tracker with FastAPI", version="1.0.0")

# Mount Static and Templates
app.mount("/static", StaticFiles(directory="frontend"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

def to_json(value):
    return json.dumps(value)

templates.env.filters["tojson"] = to_json

# CORS setup
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")

@app.get("/")
def read_root(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    if token:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
def login_page(request: Request):
    error = request.query_params.get("error")
    success = request.query_params.get("success")
    return templates.TemplateResponse("index.html", {"request": request, "action": "login", "error": error, "success": success})

@app.get("/signup")
def signup_page(request: Request):
    error = request.query_params.get("error")
    return templates.TemplateResponse("index.html", {"request": request, "action": "signup", "error": error})

@app.get("/dashboard")
def dashboard_page(request: Request, month: int = None, year: int = None, db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    if not token:
        print("Dashboard access denied: No token cookie found")
        return RedirectResponse(url="/login")
    
    try:
        current_user = get_current_user(token=token, db=db)
        print(f"Dashboard access granted for user: {current_user.email}")
        data = get_dashboard_data(db, current_user, month, year)
        return templates.TemplateResponse("dashboard.html", {"request": request, **data})
    except Exception as e:
        print(f"Dashboard error for user: {e}")
        # If it's an auth error, redirect to login
        if "credentials" in str(e).lower() or "not authenticated" in str(e).lower():
            return RedirectResponse(url="/login?error=Session+expired", status_code=status.HTTP_303_SEE_OTHER)
        # Otherwise, it might be a DB error, but we still need to handle it
        return templates.TemplateResponse("index.html", {"request": request, "error": f"An error occurred: {str(e)}"})

@app.get("/entries")
def entries_page(request: Request, month: int = None, year: int = None, db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    if not token:
        print("Entries access denied: No token cookie found")
        return RedirectResponse(url="/login")
    
    try:
        current_user = get_current_user(token=token, db=db)
        print(f"Entries access granted for user: {current_user.email}")
        
        today = date.today()
        if not year:
            year = today.year
        if not month:
            month = today.month
            
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)

        expenses = db.query(Expense).filter(
            Expense.user_id == current_user.id,
            Expense.date >= start_date,
            Expense.date <= end_date
        ).all()
        
        incomes = db.query(Income).filter(
            Income.user_id == current_user.id,
            Income.date >= start_date,
            Income.date <= end_date
        ).all()
        
        history = []
        for exp in expenses:
            history.append({
                "id": exp.id, "type": "expense", "amount": exp.amount, "category": exp.category, 
                "date": exp.date, "note": exp.note
            })
        for inc in incomes:
            history.append({
                "id": inc.id, "type": "income", "amount": inc.amount, "category": inc.category, 
                "date": inc.date, "note": inc.note
            })
            
        history.sort(key=lambda x: x['date'], reverse=True)
        categories = db.query(Category).filter(
            (Category.created_by_id == current_user.id) | (Category.created_by_id.is_(None))
        ).all()
        categories_json = [{"id": c.id, "name": c.name, "created_by_id": c.created_by_id, "type": c.type} for c in categories]
        
        return templates.TemplateResponse("entries.html", {
            "request": request, "user": current_user, "history": history, 
            "categories": categories, "categories_json": categories_json,
            "selected_month": month, "selected_year": year
        })
    except Exception as e:
        print(f"Entries error for user: {e}")
        if "credentials" in str(e).lower() or "not authenticated" in str(e).lower():
            return RedirectResponse(url="/login?error=Session+expired", status_code=status.HTTP_303_SEE_OTHER)
        return templates.TemplateResponse("index.html", {"request": request, "error": f"An error occurred: {str(e)}"})

@app.get("/edit-entry/{expense_id}")
def edit_entry_page(expense_id: int, request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/login")
    
    try:
        current_user = get_current_user(token=token, db=db)
        expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user.id).first()
        if not expense:
            return RedirectResponse(url="/entries")
        
        categories = db.query(Category).filter(
            (Category.created_by_id == current_user.id) | (Category.created_by_id.is_(None))
        ).all()
        return templates.TemplateResponse("edit_entry.html", {"request": request, "user": current_user, "expense": expense, "categories": categories})
    except Exception as e:
        print(f"Edit Entry error: {e}")
        if "credentials" in str(e).lower() or "not authenticated" in str(e).lower():
            return RedirectResponse(url="/login?error=Session+expired", status_code=status.HTTP_303_SEE_OTHER)
        return RedirectResponse(url="/login")

@app.get("/edit-income/{income_id}")
def edit_income_page(income_id: int, request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/login")
    
    try:
        current_user = get_current_user(token=token, db=db)
        income = db.query(Income).filter(Income.id == income_id, Income.user_id == current_user.id).first()
        if not income:
            return RedirectResponse(url="/entries")
        
        categories = db.query(Category).filter(
            (Category.created_by_id == current_user.id) | (Category.created_by_id.is_(None))
        ).all()
        return templates.TemplateResponse("edit_income.html", {"request": request, "user": current_user, "income": income, "categories": categories})
    except Exception as e:
        print(f"Edit Income error: {e}")
        if "credentials" in str(e).lower() or "not authenticated" in str(e).lower():
            return RedirectResponse(url="/login?error=Session+expired", status_code=status.HTTP_303_SEE_OTHER)
        return RedirectResponse(url="/login")
