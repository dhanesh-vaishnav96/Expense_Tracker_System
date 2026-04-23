
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.index import Category, Expense, Income

# Set up the database URL - same as in the app
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./expense_tracker.db")
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def remove_default_categories():
    db = SessionLocal()
    try:
        # 1. Identify default categories
        default_categories = db.query(Category).filter(Category.created_by_id.is_(None)).all()
        
        if not default_categories:
            print("No default categories found.")
            return

        print(f"Found {len(default_categories)} default categories:")
        for cat in default_categories:
            print(f" - ID: {cat.id}, Name: {cat.name}")

        default_cat_ids = [cat.id for cat in default_categories]

        # 2. Check for usage in expenses
        expenses_using = db.query(Expense).filter(Expense.category_id.in_(default_cat_ids)).all()
        expense_count = len(expenses_using)
        
        # 3. Check for usage in incomes
        incomes_using = db.query(Income).filter(Income.category_id.in_(default_cat_ids)).all()
        income_count = len(incomes_using)

        print(f"\nUsage check:")
        print(f" - Used in {expense_count} expenses")
        print(f" - Used in {income_count} incomes")

        # 4. Handle usage (set category_id to NULL for transactions using defaults)
        if expense_count > 0:
            print(f"Setting category_id to NULL for {expense_count} expenses...")
            for exp in expenses_using:
                exp.category_id = None
        
        if income_count > 0:
            print(f"Setting category_id to NULL for {income_count} incomes...")
            for inc in incomes_using:
                inc.category_id = None

        # 5. Delete the categories
        print(f"Deleting {len(default_categories)} default categories...")
        for cat in default_categories:
            db.delete(cat)
        
        db.commit()
        print("\nPermanently removed all default categories.")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    remove_default_categories()
