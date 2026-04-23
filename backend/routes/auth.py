from fastapi import APIRouter, Depends, HTTPException, status, Form, Response
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.config.database import get_db
import backend.models.index as models
import backend.schemas.index as schemas
import backend.services.auth as auth_service
from datetime import timedelta

router = APIRouter(tags=["Authentication"])

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth_service.get_password_hash(user.password)
    
    new_user = models.User(name=user.name, email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not auth_service.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login-form")
def login_form(response: Response, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    print(f"Login attempt for: {username}")
    user = db.query(models.User).filter(models.User.email == username).first()
    if not user or not auth_service.verify_password(password, user.password):
        print(f"Login failed for: {username}")
        return RedirectResponse(url="/login?error=Invalid+credentials", status_code=status.HTTP_303_SEE_OTHER)
    
    print(f"Login successful for: {username}")
    access_token_expires = timedelta(minutes=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="token", 
        value=access_token, 
        httponly=True, 
        path="/", 
        max_age=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    print(f"Cookie set for: {username}, redirecting to /dashboard")
    return response

@router.post("/register-form")
def register_form(name: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == email).first()
    if db_user:
        return RedirectResponse(url="/signup?error=Email+already+exists", status_code=status.HTTP_303_SEE_OTHER)
    
    hashed_password = auth_service.get_password_hash(password)

    new_user = models.User(name=name, email=email, password=hashed_password)
    db.add(new_user)
    db.commit()
    
    return RedirectResponse(url="/login?success=Account+created", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/logout")
def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("token", path="/")
    return response

