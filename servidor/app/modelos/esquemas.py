from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UsuarioBase(BaseModel):
    email: EmailStr
    nome_usuario: str

class UsuarioCriar(UsuarioBase):
    senha: str

class UsuarioAtualizar(BaseModel):
    email: Optional[EmailStr] = None
    nome_usuario: Optional[str] = None
    senha: Optional[str] = None

class UsuarioNoBD(UsuarioBase):
    id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True

class RespostaUsuario(BaseModel):
    status: str = "sucesso"
    dados: UsuarioNoBD
    mensagem: Optional[str] = None

class RespostaErro(BaseModel):
    status: str = "erro"
    mensagem: str
    dados: Optional[dict] = None 