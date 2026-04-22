from sqlalchemy import Column, Integer, String, Float, Date, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.config.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    total_income = Column(Float, default=1000.0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    expenses = relationship("Expense", back_populates="owner")
    incomes = relationship("Income", back_populates="owner")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    expenses = relationship("Expense", back_populates="category")
    incomes = relationship("Income", back_populates="category")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    date = Column(Date, nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")

class Income(Base):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    date = Column(Date, nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="incomes")
    category = relationship("Category", back_populates="incomes")
