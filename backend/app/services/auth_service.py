from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.utils.security import hash_password, verify_password, create_access_token
from backend.app.utils.logger import logger


def create_user(db: Session, username: str, email: str, password: str, full_name: str = "") -> User:
    existing = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if existing:
        raise ValueError("Username or email already exists")
    user = User(username=username, email=email, hashed_password=hash_password(password), full_name=full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"Created user: {username}")
    return user


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def generate_token(user: User) -> str:
    return create_access_token(data={"sub": str(user.id), "username": user.username, "role": user.role})


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user: User, full_name: str = None, email: str = None) -> User:
    if full_name is not None:
        user.full_name = full_name
    if email is not None:
        user.email = email
    db.commit()
    db.refresh(user)
    return user
