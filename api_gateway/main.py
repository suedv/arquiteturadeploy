from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import requests
from typing import Optional, Any
from pydantic import BaseModel
from starlette.responses import Response
import jwt
from datetime import datetime, timedelta
import hashlib
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResponseModel(BaseModel):
    status: str
    data: Optional[Any] = None
    message: Optional[str] = None

# Configurações de autenticação
SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta_aqui")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Simular banco de usuários (em produção, usar banco real)
USERS_DB = {
    "admin": {
        "username": "admin",
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin"
    },
    "user": {
        "username": "user",
        "password": hashlib.sha256("user123".encode()).hexdigest(),
        "role": "user"
    }
}

# URL do Load Balancer
LOAD_BALANCER_URL = os.getenv("LOAD_BALANCER_URL", "http://localhost:8001")

security = HTTPBearer()

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    role: str = "user"

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/saude")
def saude():
    return ResponseModel(
        status="success",
        data={
            "status": "saudavel",
            "servico": "api-gateway",
            "load_balancer": LOAD_BALANCER_URL
        }
    )

@app.post("/register", response_model=ResponseModel)
def register(user: UserRegister):
    if user.username in USERS_DB:
        return ResponseModel(
            status="error",
            message="Usuário já existe"
        )
    
    USERS_DB[user.username] = {
        "username": user.username,
        "password": hashlib.sha256(user.password.encode()).hexdigest(),
        "role": user.role
    }
    
    return ResponseModel(
        status="success",
        message="Usuário registrado com sucesso"
    )

@app.post("/login", response_model=ResponseModel)
def login(user: UserLogin):
    if user.username not in USERS_DB:
        return ResponseModel(
            status="error",
            message="Usuário não encontrado"
        )
    
    stored_user = USERS_DB[user.username]
    if stored_user["password"] != hashlib.sha256(user.password.encode()).hexdigest():
        return ResponseModel(
            status="error",
            message="Senha incorreta"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": stored_user["role"]}, 
        expires_delta=access_token_expires
    )
    
    return ResponseModel(
        status="success",
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    )

@app.middleware("http")
async def proxy_to_load_balancer(request: Request, call_next):
    # Se for uma requisição para endpoints de autenticação, não fazer proxy
    if request.url.path in ["/saude", "/register", "/login", "/docs", "/openapi.json"]:
        return await call_next(request)
    
    # Verificar autenticação para rotas protegidas
    if request.url.path.startswith("/itens"):
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return Response(
                    content=ResponseModel(
                        status="error",
                        message="Token de autenticação necessário"
                    ).model_dump_json(),
                    status_code=401,
                    media_type="application/json"
                )
            
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            
            if username not in USERS_DB:
                return Response(
                    content=ResponseModel(
                        status="error",
                        message="Usuário não encontrado"
                    ).model_dump_json(),
                    status_code=401,
                    media_type="application/json"
                )
            
            logger.info(f"Usuário autenticado: {username} - Requisição: {request.method} {request.url.path}")
            
        except jwt.ExpiredSignatureError:
            return Response(
                content=ResponseModel(
                    status="error",
                    message="Token expirado"
                ).model_dump_json(),
                status_code=401,
                media_type="application/json"
            )
        except jwt.JWTError:
            return Response(
                content=ResponseModel(
                    status="error",
                    message="Token inválido"
                ).model_dump_json(),
                status_code=401,
                media_type="application/json"
            )
    
    try:
        # Construir a URL completa para o Load Balancer
        target_url = f"{LOAD_BALANCER_URL}{request.url.path}"
        if request.url.query:
            target_url += f"?{request.url.query}"
        
        # Fazer a requisição para o Load Balancer
        method = request.method
        headers = dict(request.headers)
        body = await request.body()
        
        response = requests.request(
            method=method,
            url=target_url,
            headers=headers,
            data=body,
            timeout=30
        )
        
        logger.info(f"Resposta do Load Balancer: {response.status_code}")
        
        # Retornar a resposta do Load Balancer
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
    except Exception as e:
        logger.error(f"Erro ao conectar com Load Balancer: {str(e)}")
        return Response(
            content=ResponseModel(
                status="error",
                message=f"Erro ao conectar com Load Balancer: {str(e)}"
            ).model_dump_json(),
            status_code=500,
            media_type="application/json"
        ) 