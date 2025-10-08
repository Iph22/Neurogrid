# backend/routers/auth.py
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel

from ..database import models, database, schemas

# ---------------------------
# CONFIG
# ---------------------------
SECRET_KEY = "neurogrid_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter()
pwd_context = CryptContext(schemes=["Argon2"], deprecated="auto")

# ---------------------------
# SCHEMAS
# ---------------------------


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    username: str
    password: str

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# ---------------------------
# ROUTES
# ---------------------------


@router.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Ensure username is provided
    if not user.username or not user.username.strip():
        raise HTTPException(
            status_code=400, detail="Username is required")
    
    # Check if username already exists
    db_user = get_user(db, user.username)
    if db_user:
        raise HTTPException(
            status_code=400, detail="Username already registered")
    
    # Truncate password to 72 characters to prevent bcrypt errors
    truncated_password = user.password[:72]
    hashed_pw = get_password_hash(truncated_password)
    new_user = models.User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login_user(request: LoginRequest, db: Session = Depends(database.get_db)):
    # Ensure username and password are provided
    if not request.username or not request.username.strip():
        raise HTTPException(status_code=400, detail="Username is required")
    if not request.password:
        raise HTTPException(status_code=400, detail="Password is required")
    
    user = get_user(db, request.username)
    # Truncate password to 72 characters for consistency with registration
    truncated_password = request.password[:72]
    if not user or not verify_password(truncated_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401, detail="Invalid authentication token")
        user = get_user(db, username=username)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(
            status_code=401, detail="Invalid authentication token")
