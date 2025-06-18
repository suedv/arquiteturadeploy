from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import TypeVar, Generic, Optional, Any

load_dotenv()

app = FastAPI(title="Servidor de Aplicação 2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/dbname")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    status: str
    data: Optional[T] = None
    message: Optional[str] = None

class Item(Base):
    __tablename__ = "itens"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(String(500))
    preco = Column(Float, nullable=False)

Base.metadata.create_all(bind=engine)

class ItemCreate(BaseModel):
    nome: str
    descricao: str | None = None
    preco: float

class ItemResponse(BaseModel):
    id: int
    nome: str
    descricao: str | None
    preco: float
    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def item_to_dict(item: Item) -> dict:
    """Converte um objeto Item para dicionário"""
    return {
        "id": item.id,
        "nome": item.nome,
        "descricao": item.descricao,
        "preco": item.preco
    }

@app.get("/saude")
def saude():
    porta = os.getenv("PORTA", "8003")
    return ResponseModel(
        status="success",
        data={"status": "saudavel", "servidor": f"Server 2 - Porta {porta}"}
    )

@app.post("/itens")
def criar_item(item: ItemCreate, db: Session = Depends(get_db)):
    try:
        novo = Item(**item.dict())
        db.add(novo)
        db.commit()
        db.refresh(novo)
        return ResponseModel(
            status="success",
            data=item_to_dict(novo)
        )
    except Exception as e:
        return ResponseModel(
            status="error",
            message=str(e)
        )

@app.get("/itens")
def listar_itens(db: Session = Depends(get_db)):
    try:
        itens = db.query(Item).all()
        itens_dict = [item_to_dict(item) for item in itens]
        return ResponseModel(
            status="success",
            data=itens_dict
        )
    except Exception as e:
        return ResponseModel(
            status="error",
            message=str(e)
        )

@app.get("/itens/{item_id}")
def obter_item(item_id: int, db: Session = Depends(get_db)):
    try:
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            return ResponseModel(
                status="error",
                message="Item não encontrado"
            )
        return ResponseModel(
            status="success",
            data=item_to_dict(item)
        )
    except Exception as e:
        return ResponseModel(
            status="error",
            message=str(e)
        )

@app.put("/itens/{item_id}")
def atualizar_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db)):
    try:
        obj = db.query(Item).filter(Item.id == item_id).first()
        if not obj:
            return ResponseModel(
                status="error",
                message="Item não encontrado"
            )
        for k, v in item.dict().items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
        return ResponseModel(
            status="success",
            data=item_to_dict(obj)
        )
    except Exception as e:
        return ResponseModel(
            status="error",
            message=str(e)
        )

@app.delete("/itens/{item_id}")
def remover_item(item_id: int, db: Session = Depends(get_db)):
    try:
        obj = db.query(Item).filter(Item.id == item_id).first()
        if not obj:
            return ResponseModel(
                status="error",
                message="Item não encontrado"
            )
        db.delete(obj)
        db.commit()
        return ResponseModel(
            status="success",
            message="Item removido com sucesso"
        )
    except Exception as e:
        return ResponseModel(
            status="error",
            message=str(e)
        )

@app.get("/identidade")
def identidade():
    porta = os.getenv("PORTA", "8003")
    return ResponseModel(
        status="success",
        data={"servidor": f"Server 2 - Porta {porta}"}
    ) 