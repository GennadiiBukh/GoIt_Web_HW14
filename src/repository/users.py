from sqlalchemy.orm import Session
from src.database.models import User
from src.services.auth import get_password_hash

def get_user_by_email(db: Session, email: str) -> User:
    """
    The get_user_by_email function takes in a database session and an email address, and returns the user with that email address.

    :param db: Session: Pass the database session to the function
    :param email: str: Filter the users by email
    :return: A user object
    :doc-Author: BGU
    """
    return db.query(User).filter(User.email == email).first()

def register_user(db: Session, username: str, email: str, hashed_password: str) -> User:
    """
    The register_user function takes in a database session, username, email, and hashed password, and returns a user object.

    :param db: Session: Pass the database session to the function
    :param username: str: Get the username from the request
    :param email: str: Get the email from the request
    :param hashed_password: str: Hash the password
    :return: A user object
    :doc-Author: BGU
    """
    db_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def confirm_email(db: Session, email: str):
    """
    The confirm_email function takes in a database session and an email address, and sets the confirmed field of the user with that email address to True.

    :param db: Session: Pass the database session to the function
    :param email: str: Get the email from the request
    :return: None
    :doc-Author: BGU
    """
    db_user = get_user_by_email(db, email)
    if db_user:
        db_user.confirmed = True
        db.commit()



