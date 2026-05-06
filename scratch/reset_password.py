from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.index import User
from backend.config.database import SQLALCHEMY_DATABASE_URL
import backend.services.auth as auth_service

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

email = 'dhaneshvaishnav123@gmail.com'
new_password = "password123"

user = db.query(User).filter(User.email == email).first()
if user:
    print(f"User found: {user.email}")
    hashed_password = auth_service.get_password_hash(new_password)
    user.password = hashed_password
    db.commit()
    print(f"Password reset for {email} to {new_password}")
else:
    print(f"User {email} not found.")

db.close()
