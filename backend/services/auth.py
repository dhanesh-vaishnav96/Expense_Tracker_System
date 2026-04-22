from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyCookie
from sqlalchemy.orm import Session
from backend.config.database import get_db
import backend.models.index as models
import backend.schemas.index as schemas
import os
from starlette.responses import RedirectResponse

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-that-should-be-in-env")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)
cookie_scheme = APIKeyCookie(name="token", auto_error=False)


# Password Hashing
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Token Generation
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Get Current User
def get_current_user(token: str = Depends(cookie_scheme), bearer_token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Prefer cookie token for SSR
    final_token = token or bearer_token
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not final_token:
        # For SSR, we might want to redirect instead of raising 401
        # But for now, we'll let the route handle redirects if needed
        raise credentials_exception

    try:
        payload = jwt.decode(final_token, SECRET_KEY, algorithms=[ALGORITHM])

        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user
