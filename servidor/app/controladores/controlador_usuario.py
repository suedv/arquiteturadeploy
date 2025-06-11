from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..modelos.base import obter_db
from ..modelos.usuario import Usuario
from ..modelos.esquemas import UsuarioCriar, UsuarioAtualizar, RespostaUsuario, RespostaErro
from passlib.context import CryptContext

roteador = APIRouter()
contexto_senha = CryptContext(schemes=["bcrypt"], deprecated="auto")

def obter_hash_senha(senha: str) -> str:
    return contexto_senha.hash(senha)

@roteador.post("/usuarios", response_model=RespostaUsuario, status_code=status.HTTP_201_CREATED)
def criar_usuario(usuario: UsuarioCriar, db: Session = Depends(obter_db)):
    db_usuario = Usuario(
        email=usuario.email,
        nome_usuario=usuario.nome_usuario,
        senha_hash=obter_hash_senha(usuario.senha)
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return RespostaUsuario(dados=db_usuario, mensagem="Usuário criado com sucesso")

@roteador.get("/usuarios", response_model=List[RespostaUsuario])
def listar_usuarios(pular: int = 0, limite: int = 100, db: Session = Depends(obter_db)):
    usuarios = db.query(Usuario).offset(pular).limit(limite).all()
    return [RespostaUsuario(dados=usuario) for usuario in usuarios]

@roteador.get("/usuarios/{usuario_id}", response_model=RespostaUsuario)
def obter_usuario(usuario_id: int, db: Session = Depends(obter_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return RespostaUsuario(dados=usuario)

@roteador.put("/usuarios/{usuario_id}", response_model=RespostaUsuario)
def atualizar_usuario(usuario_id: int, usuario: UsuarioAtualizar, db: Session = Depends(obter_db)):
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    dados_atualizacao = usuario.dict(exclude_unset=True)
    if "senha" in dados_atualizacao:
        dados_atualizacao["senha_hash"] = obter_hash_senha(dados_atualizacao.pop("senha"))
    
    for chave, valor in dados_atualizacao.items():
        setattr(db_usuario, chave, valor)
    
    db.commit()
    db.refresh(db_usuario)
    return RespostaUsuario(dados=db_usuario, mensagem="Usuário atualizado com sucesso")

@roteador.delete("/usuarios/{usuario_id}", response_model=RespostaUsuario)
def remover_usuario(usuario_id: int, db: Session = Depends(obter_db)):
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    db.delete(db_usuario)
    db.commit()
    return RespostaUsuario(dados=db_usuario, mensagem="Usuário removido com sucesso") 