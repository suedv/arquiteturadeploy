from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv
from typing import List
import itertools
import logging
import time
from datetime import datetime, timedelta

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

app = FastAPI(title="Load Balancer")

# Configuração do middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lista de servidores disponíveis
SERVIDORES = os.getenv("SERVIDORES", "http://localhost:8002,http://localhost:8003").split(",")
servidor_atual = itertools.cycle(SERVIDORES)

# Cache de status dos servidores
servidor_status = {servidor: {"ultimo_check": None, "saudavel": True} for servidor in SERVIDORES}

def verificar_saude_servidor(servidor: str) -> bool:
    """Verifica a saúde de um servidor específico."""
    try:
        response = requests.get(f"{servidor}/saude", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def atualizar_status_servidores():
    """Atualiza o status de todos os servidores."""
    for servidor in SERVIDORES:
        agora = datetime.now()
        ultimo_check = servidor_status[servidor]["ultimo_check"]
        
        # Verifica a cada 30 segundos
        if not ultimo_check or (agora - ultimo_check) > timedelta(seconds=30):
            servidor_status[servidor]["saudavel"] = verificar_saude_servidor(servidor)
            servidor_status[servidor]["ultimo_check"] = agora

def obter_proximo_servidor_saudavel() -> str:
    """Obtém o próximo servidor saudável usando round-robin."""
    atualizar_status_servidores()
    servidores_saudaveis = [s for s in SERVIDORES if servidor_status[s]["saudavel"]]
    
    if not servidores_saudaveis:
        raise HTTPException(status_code=503, detail="Nenhum servidor disponível")
    
    # Encontra o próximo servidor saudável
    while True:
        servidor = next(servidor_atual)
        if servidor in servidores_saudaveis:
            return servidor

@app.middleware("http")
async def balancear_carga(request: Request, call_next):
    """Middleware para balancear carga entre os servidores disponíveis."""
    try:
        # Seleciona o próximo servidor saudável
        servidor = obter_proximo_servidor_saudavel()
        logger.info(f"Encaminhando requisição para: {servidor}")
        
        # Encaminha a requisição para o servidor selecionado
        response = requests.request(
            method=request.method,
            url=f"{servidor}{request.url.path}",
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
    atualizar_status_servidores()
    return {
        "status": "saudavel",
        "servico": "load-balancer",
        "servidores": {
            servidor: {
                "saudavel": status["saudavel"],
                "ultimo_check": status["ultimo_check"].isoformat() if status["ultimo_check"] else None
            }
            for servidor, status in servidor_status.items()
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 