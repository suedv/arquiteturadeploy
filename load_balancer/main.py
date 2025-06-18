from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
from typing import Optional, Any
from pydantic import BaseModel
from starlette.responses import Response
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Load Balancer")

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

# Lista de servidores para balanceamento
SERVIDORES = os.getenv("SERVIDORES", "http://localhost:8002,http://localhost:8003").split(",")
current_server_index = 0

logger.info(f"Load Balancer iniciado com servidores: {SERVIDORES}")

@app.get("/saude")
def saude():
    return ResponseModel(
        status="success",
        data={
            "status": "saudavel",
            "servico": "load-balancer",
            "servidores": SERVIDORES,
            "servidor_atual": current_server_index
        }
    )

@app.middleware("http")
async def proxy_to_server(request: Request, call_next):
    global current_server_index
    
    # Se for uma requisição para /saude, não fazer proxy
    if request.url.path == "/saude":
        return await call_next(request)
    
    try:
        # Selecionar o próximo servidor (round-robin)
        server_url = SERVIDORES[current_server_index]
        current_server_index = (current_server_index + 1) % len(SERVIDORES)
        
        logger.info(f"Requisição {request.method} {request.url.path} -> Servidor {current_server_index}: {server_url}")
        
        # Construir a URL completa
        target_url = f"{server_url}{request.url.path}"
        if request.url.query:
            target_url += f"?{request.url.query}"
        
        # Fazer a requisição para o servidor
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
        
        logger.info(f"Resposta do servidor {server_url}: {response.status_code}")
        
        # Retornar a resposta do servidor diretamente
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
    except Exception as e:
        logger.error(f"Erro ao conectar com servidor {server_url}: {str(e)}")
        return ResponseModel(
            status="error",
            message=f"Erro ao conectar com servidor: {str(e)}"
        ) 