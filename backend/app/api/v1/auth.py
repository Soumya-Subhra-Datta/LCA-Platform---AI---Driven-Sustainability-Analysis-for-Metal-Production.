from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas.user import UserCreate, UserLogin, UserResponse, Token, UserUpdate
from backend.app.services import auth_service
from backend.app.api.v1.deps import get_current_user
from backend.app.models.user import User
from backend.app.utils.validators import validate_email, validate_password
from backend.app.utils.logger import logger

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if not validate_email(user.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    is_valid, msg = validate_password(user.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)
    try:
        db_user = auth_service.create_user(db, user.username, user.email, user.password, user.full_name)
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, credentials.identifier, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth_service.generate_token(user)
    return Token(access_token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
def update_profile(update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    updated = auth_service.update_user(db, current_user, full_name=update.full_name, email=update.email)
    return UserResponse.model_validate(updated)
