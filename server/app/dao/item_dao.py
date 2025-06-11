from sqlalchemy.orm import Session
from ..models.item import Item
from typing import List, Optional

class ItemDAO:
    """Data Access Object para o modelo Item."""
    
    def __init__(self, db: Session):
        self.db = db

    def criar(self, item: Item) -> Item:
        """Cria um novo item."""
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def obter_por_id(self, item_id: int) -> Optional[Item]:
        """Obtém um item pelo ID."""
        return self.db.query(Item).filter(Item.id == item_id).first()

    def listar(self) -> List[Item]:
        """Lista todos os itens."""
        return self.db.query(Item).all()

    def atualizar(self, item: Item) -> Item:
        """Atualiza um item existente."""
        self.db.commit()
        self.db.refresh(item)
        return item

    def remover(self, item: Item) -> None:
        """Remove um item."""
        self.db.delete(item)
        self.db.commit() 