from dotenv import load_dotenv

load_dotenv()
import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "")
DATABASE_NAME = os.getenv("DATABASE_NAME", "")

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}"))
    conn.commit()

engine = create_engine(DATABASE_URL + f"/{DATABASE_NAME}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
