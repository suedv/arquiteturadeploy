from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv
from typing import List
import itertools

# Carrega variáveis de ambiente
load_dotenv()

app = FastAPI(title="Balanceador de Carga")

# Configuração do middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lista de servidores a partir das variáveis de ambiente
SERVIDORES = os.getenv("SERVIDORES", "http://localhost:8002,http://localhost:8003").split(",")
ciclo_servidores = itertools.cycle(SERVIDORES)

@app.middleware("http")
async def middleware_balanceador(request: Request, call_next):
    """Middleware para distribuir requisições entre os servidores disponíveis."""
    try:
        # Obtém o próximo servidor no estilo round-robin
        servidor = next(ciclo_servidores)
        
        # Encaminha a requisição para o servidor selecionado
        resposta = requests.request(
            method=request.method,
            url=f"{servidor}{request.url.path}",
            headers=dict(request.headers),
            params=dict(request.query_params),
            data=await request.body()
        )
        
        return resposta
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail="Serviço indisponível")

@app.get("/saude")
async def verificar_saude():
    """Endpoint de verificação de saúde."""
    return {
        "status": "saudavel",
        "servico": "balanceador-de-carga",
        "servidores": SERVIDORES
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 