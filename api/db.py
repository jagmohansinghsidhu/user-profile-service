import os

from sqlmodel import create_engine, Session
from sqlalchemy.orm import sessionmaker

from .models import create_all

DB_USER = os.environ.get('DB_USER', 'lb')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'password')
DB_HOST = os.environ.get('DB_HOST', 'localhost:3306')
DB_NAME = os.environ.get('DB_NAME', 'lb')

connection_string = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"


engine = create_engine(connection_string)

create_all(engine)

SessionLocal = sessionmaker(bind=engine, class_=Session)


def get_db_session():

    with SessionLocal() as session:
        yield session
