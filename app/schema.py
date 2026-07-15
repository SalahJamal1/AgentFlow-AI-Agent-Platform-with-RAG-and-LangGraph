from pydantic import BaseModel


class CreateUsers(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str


class CreateConversations(BaseModel):
    title: str


class CreateMessages(BaseModel):
    content: str
