from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from BACKEND.Config.config import DATABASE_URL



print("DATABASE_URL:", DATABASE_URL)
engine = create_engine(DATABASE_URL)
session_local = sessionmaker(autoflush=False,autocommit=False,bind=engine)
Base = declarative_base() 

