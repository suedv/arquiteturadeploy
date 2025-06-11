from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv
from typing import Optional
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

app = FastAPI(title="API Gateway")

# Configuração do middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações
SECRET_KEY = os.getenv("SECRET_KEY", "chave_secreta_temporaria")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
LOAD_BALANCER_URL = os.getenv("LOAD_BALANCER_URL", "http://localhost:8001")

# Dependência para autenticação
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Simulação de banco de dados de usuários (em produção, use um banco real)
USERS_DB = {
    "usuario": {
        "username": "usuario",
        "password": "senha123",  # Em produção, use hash de senha
        "disabled": False
    }
}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = USERS_DB.get(username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = USERS_DB.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Requisição recebida: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Resposta enviada: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Erro na requisição: {str(e)}")
        raise

@app.middleware("http")
async def route_requests(request: Request, call_next):
    """Middleware para rotear requisições para o balanceador de carga."""
    if request.url.path == "/token" or request.url.path == "/docs" or request.url.path == "/openapi.json":
        return await call_next(request)

    try:
        # Encaminha a requisição para o balanceador de carga
        response = requests.request(
            method=request.method,
            url=f"{LOAD_BALANCER_URL}{request.url.path}",
            headers=dict(request.headers),
            params=dict(request.query_params),
            data=await request.body()
        )
        
        return response
    except requests.RequestException as e:
        logger.error(f"Erro ao encaminhar requisição: {str(e)}")
        raise HTTPException(status_code=503, detail="Serviço indisponível")

@app.get("/saude")
async def verificar_saude():
    """Endpoint de verificação de saúde."""
    return {"status": "saudavel", "servico": "api-gateway"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 