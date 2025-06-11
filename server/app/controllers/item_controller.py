from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..dao.item_dao import ItemDAO
from ..models.item import Item
from ..database import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/itens", tags=["itens"])

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

@router.post("/", response_model=ItemResponse)
def criar_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Cria um novo item."""
    dao = ItemDAO(db)
    novo_item = Item(**item.model_dump())
    return dao.criar(novo_item)

@router.get("/", response_model=List[ItemResponse])
def listar_itens(db: Session = Depends(get_db)):
    """Lista todos os itens."""
    dao = ItemDAO(db)
    return dao.listar()

@router.get("/{item_id}", response_model=ItemResponse)
def obter_item(item_id: int, db: Session = Depends(get_db)):
    """Obtém um item pelo ID."""
    dao = ItemDAO(db)
    item = dao.obter_por_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item

@router.put("/{item_id}", response_model=ItemResponse)
def atualizar_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db)):
    """Atualiza um item existente."""
    dao = ItemDAO(db)
    item_existente = dao.obter_por_id(item_id)
    if not item_existente:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    for key, value in item.model_dump().items():
        setattr(item_existente, key, value)
    
    return dao.atualizar(item_existente)

@router.delete("/{item_id}")
def remover_item(item_id: int, db: Session = Depends(get_db)):
    """Remove um item."""
    dao = ItemDAO(db)
    item = dao.obter_por_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    dao.remover(item)
    return {"message": "Item removido com sucesso"} 