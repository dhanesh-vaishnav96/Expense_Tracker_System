import sys
import os

# Add the project root to sys.path to import backend modules
sys.path.append(os.getcwd())

from backend.config.database import SessionLocal, engine
from backend.models.index import User, Expense, Income, Category

def delete_all_records():
    db = SessionLocal()
    try:
        print("Deleting all expenses...")
        db.query(Expense).delete()
        
        print("Deleting all incomes...")
        db.query(Income).delete()
        
        print("Deleting all categories...")
        db.query(Category).delete()
        
        print("Deleting all users...")
        db.query(User).delete()
        
        db.commit()
        print("Successfully deleted all accounts and related records.")
    except Exception as e:
        db.rollback()
        print(f"Error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    delete_all_records()
