import os
import sys
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine, text
from backend.config.database import SQLALCHEMY_DATABASE_URL, engine

print('Connecting to:', SQLALCHEMY_DATABASE_URL)
with engine.connect() as conn:
    if 'sqlite' in SQLALCHEMY_DATABASE_URL:
        print('Using SQLite')
    else:
        # Postgres
        result = conn.execute(text("""
            SELECT conname
            FROM pg_constraint
            WHERE conrelid = 'categories'::regclass
            AND contype = 'u';
        """))
        constraints = [row[0] for row in result]
        print('Unique constraints on categories:', constraints)
        for c in constraints:
            conn.execute(text(f'ALTER TABLE categories DROP CONSTRAINT {c}'))
            print(f'Dropped {c}')
        
        # Also check for unique indexes
        result = conn.execute(text("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'categories'
            AND indexdef LIKE '%UNIQUE%';
        """))
        indexes = [row[0] for row in result]
        print('Unique indexes on categories:', indexes)
        for idx in indexes:
            if idx != 'categories_pkey':
                conn.execute(text(f'DROP INDEX {idx}'))
                print(f'Dropped index {idx}')
        conn.commit()
