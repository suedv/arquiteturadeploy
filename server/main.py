from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import item_controller
from app.models.base import Base
from app.database import engine
import os
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Servidor de Aplicação")

# Configuração do middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui os routers
app.include_router(item_controller.router)

@app.get("/saude")
async def verificar_saude():
    """Endpoint de verificação de saúde."""
    return {
        "status": "saudavel",
        "servico": "servidor",
        "id": os.getenv("SERVER_ID", "1")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 