from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from os import getenv


engine = create_engine(getenv("DATABASE_URL"))
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass

class NotFoundError(Exception):
    pass

# Dependency to get the database session
def get_db():
    database = session_local()
    try:
        yield database
    finally:
        database.close()
