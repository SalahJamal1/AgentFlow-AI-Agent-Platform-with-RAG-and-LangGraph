from dotenv import load_dotenv

load_dotenv()
import os
from datetime import timedelta, datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Users
from app.schema import CreateUsers

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")
SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHMS = os.getenv("ALGORITHM", "")
Issuer = os.getenv("ISSUER", "")
AUDIENCE = os.getenv("AUDIENCE", "")


def create_access_token(user: Users):
    expires = datetime.now(timezone.utc) + timedelta(minutes=30)

    encoded = {
        "sub": user.email,
        "id": user.id,
        "exp": expires,
        "iss": Issuer,
        "aud": AUDIENCE,
    }

    return jwt.encode(
        encoded,
        SECRET_KEY,
        algorithm=ALGORITHMS,
    )


def get_current_user(token: str):
    try:

        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHMS], audience=AUDIENCE, issuer=Issuer
        )
        id = payload.get("id", None)
        email = payload.get("sub", None)
        if id is None or email is None:
            raise HTTPException(
                status_code=400, detail="Could not validate credentials"
            )
        return {"email": email, "id": id}
    except JWTError as e:
        raise HTTPException(
            status_code=400, detail=f"Could not validate credentials - {e}"
        )


def check_user_and_password(db: db_dependency, email: str, password: str):
    user = db.query(Users).filter(Users.email == email).first()

    if not user or not bcrypt.verify(password, user.password):
        return False
    return user


@router.post("/register")
def register(db: db_dependency, new_user: CreateUsers):
    try:
        existing_user = db.query(Users).filter(Users.email == new_user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        if new_user.password != new_user.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords don't match")
        user = Users(
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            email=new_user.email,
        )
        user.password = bcrypt.hash(new_user.password)

        db.add(user)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"something went wrong - {e}")


@router.post("/login")
def login(
        db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    try:
        user = check_user_and_password(db, form_data.username, form_data.password)

        if not user:
            raise HTTPException(
                status_code=400, detail="Incorrect username or password"
            )

        token = create_access_token(user)
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"something went wrong - {e}")
