from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, EmailStr

Base = declarative_base()

class User(Base):
    """Modelo de usuário para o banco de dados"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

class UserBase(BaseModel):
    """Modelo base para usuário"""
    email: EmailStr
    username: str

class UserCreate(UserBase):
    """Modelo para criação de usuário"""
    password: str

class UserResponse(UserBase):
    """Modelo para resposta de usuário"""
    id: int
    is_active: bool

    class Config:
        orm_mode = True 