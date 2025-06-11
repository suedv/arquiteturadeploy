from sqlalchemy import Column, String, Float
from .base import ModeloBase

class Item(ModeloBase):
    """Modelo para representar um item."""
    __tablename__ = "itens"

    nome = Column(String(100), nullable=False)
    descricao = Column(String(500))
    preco = Column(Float, nullable=False) 