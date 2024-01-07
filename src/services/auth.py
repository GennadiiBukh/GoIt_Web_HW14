import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import User

from fastapi.security import OAuth2PasswordBearer

from dotenv import load_dotenv

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/auth/token")

# Налаштування для хешування паролів
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

secret_key = os.environ.get('SECRET_KEY_JWT')
algorithm = os.environ.get('ALGORITHM')


def verify_password(plain_password, hashed_password):
    """
    The verify_password function takes in a plain text password and a hashed password
    and returns True if the password is correct, False otherwise

    :param plain_password: The password that the user entered
    :param hashed_password: The hashed password stored in the database
    :return: A boolean value
    :doc-Author: BGU
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    The get_password_hash function takes a password as input and returns a hashed version of that password.

    :param password: The password to be hashed
    :return: The hashed password
    :doc-Author: BGU
    """
    return pwd_context.hash(password)


def authenticate_user(db: Session, email: str, password: str):
    """
    The authenticate_user function takes in an email and password, and returns a user object if the user exists in the database.

    :param db: Session: Pass the database session to the function
    :param email: str: Get the email from the request
    :param password: str: Get the password from the request
    :return: A user object
    :doc-Author: BGU
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    The create_access_token function takes in a data dictionary and an optional expires_delta
    parameter. The expires_delta parameter is used to set the expiration time of the token.

    :param data: dict: Pass the data dictionary to the function
    :param expires_delta: timedelta: Set the expiration time of the token
    :return: A token
    :doc-Author: BGU
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    """
    The create_refresh_token function takes in a data dictionary and an optional expires_delta
    parameter. The expires_delta parameter is used to set the expiration time of the token.

    :param data: dict: Pass the data dictionary to the function
    :param expires_delta: timedelta: Set the expiration time of the token
    :return: A token
    :doc-Author: BGU
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)  # Довший час життя
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    The get_current_user function is used to get the current user from the token.

    :param token: str: Get the token from the request
    :param db: Session: Pass the database session to the function
    :return: A user object
    :doc-Author: BGU
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


def create_email_token(data: dict):
    """
    The create_email_token function takes in a data dictionary and returns
    an encoded token. The token is created using the secret key and algorithm.

    :param data: dict: Pass the data dictionary to the function
    :return: A token
    :doc-Author: BGU
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def get_email_from_token(token: str) -> str:
    """
    The get_email_from_token function takes in a token and returns the email associated with it.

    :param token: str: Pass the token to the function
    :return: A string
    :doc-Author: BGU
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token for email verification")
        return email
    except JWTError as e:
        print(e)
        raise HTTPException(status_code=401, detail="Invalid token for email verification")

