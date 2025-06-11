from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Servidor de Aplicação")

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

@app.get("/saude")
def saude():
    porta = os.getenv("PORTA", "8002")
    return {"status": "saudavel", "servidor": porta}

@app.post("/itens", response_model=ItemResponse)
def criar_item(item: ItemCreate, db: Session = Depends(get_db)):
    novo = Item(**item.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@app.get("/itens", response_model=list[ItemResponse])
def listar_itens(db: Session = Depends(get_db)):
    return db.query(Item).all()

@app.get("/itens/{item_id}", response_model=ItemResponse)
def obter_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item

@app.put("/itens/{item_id}", response_model=ItemResponse)
def atualizar_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db)):
    obj = db.query(Item).filter(Item.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    for k, v in item.dict().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@app.delete("/itens/{item_id}")
def remover_item(item_id: int, db: Session = Depends(get_db)):
    obj = db.query(Item).filter(Item.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    db.delete(obj)
    db.commit()
    return {"message": "Item removido com sucesso"}

@app.get("/identidade")
def identidade():
    porta = os.getenv("PORTA", "desconhecido")
    return {"servidor": porta} 