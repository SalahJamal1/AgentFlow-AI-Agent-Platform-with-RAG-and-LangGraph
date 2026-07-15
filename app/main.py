from dotenv import load_dotenv

from app.database import engine, Base
from app.router import auth, chats

load_dotenv()
from fastapi import FastAPI

app = FastAPI()

Base.metadata.create_all(engine)

app.include_router(auth.router)
app.include_router(chats.router)
