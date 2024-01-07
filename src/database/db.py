import os
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get('DB_URL')

# Підключення до бази даних
engine = create_engine(db_url)
db_Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base: DeclarativeMeta = declarative_base()

def get_db():
    """
    The get_db function returns a database session
    :return: A session object
    :doc-Author: BGU
    """
    db = db_Session()
    try:
        yield db
    finally:
        db.close()


def create_database_tables():
    """
    The create_database_tables function creates all tables in the database
    :return: None
    :doc-Author: BGU
    """
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Error creating database tables: {e}")


