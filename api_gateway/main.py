from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
import requests
from starlette.responses import Response
from dotenv import load_dotenv
from typing import Optional, Any
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
LOAD_BALANCER_URL = os.getenv("LOAD_BALANCER_URL", "http://localhost:8001")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

USERS_DB = {"usuario": {"username": "usuario", "password": "senha123"}}

class ResponseModel(BaseModel):
    status: str
    data: Optional[Any] = None
    message: Optional[str] = None

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail="Credenciais inválidas")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None or username not in USERS_DB:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return USERS_DB[username]

@app.post("/token", response_model=ResponseModel)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = USERS_DB.get(form_data.username)
        if not user or user["password"] != form_data.password:
            return ResponseModel(
                status="error",
                message="Usuário ou senha incorretos"
            )
        access_token = create_access_token({"sub": user["username"]}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return ResponseModel(
            status="success",
            data={"access_token": access_token, "token_type": "bearer"}
        )
    except Exception as e:
        return ResponseModel(
            status="error",
            message=str(e)
        )

@app.middleware("http")
async def proxy_to_lb(request: Request, call_next):
    if request.url.path in ["/token", "/docs", "/openapi.json", "/saude"]:
        return await call_next(request)
    try:
        resp = requests.request(
            method=request.method,
            url=f"{LOAD_BALANCER_URL}{request.url.path}",
            headers={k: v for k, v in request.headers.items() if k != 'host'},
            params=dict(request.query_params),
            data=await request.body()
        )
        return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))
    except Exception as e:
        return ResponseModel(
            status="error",
            message="Serviço indisponível"
        ).dict()

@app.get("/saude", response_model=ResponseModel)
async def saude():
    return ResponseModel(
        status="success",
        data={"status": "saudavel", "servico": "api-gateway"}
    ) 