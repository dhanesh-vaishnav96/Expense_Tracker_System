from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from backend.models.index import User, Expense, Category
from backend.config.database import SQLALCHEMY_DATABASE_URL
from datetime import date

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

user = db.query(User).first()
if user:
    print(f"Testing for user: {user.email}")
    year = date.today().year
    month = date.today().month
    
    try:
        # Test year extract
        year_val = db.query(func.extract('year', Expense.date)).filter(Expense.user_id == user.id).first()
        print(f"Extracted year value type: {type(year_val[0]) if year_val else 'No expenses'}")
        
        # Test filtering
        expenses = db.query(Expense).filter(
            Expense.user_id == user.id,
            func.extract('year', Expense.date) == year
        ).all()
        print(f"Expenses found for year {year}: {len(expenses)}")
    except Exception as e:
        print(f"Error extracting year: {e}")
else:
    print("No user found in database.")

db.close()
