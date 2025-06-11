from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI(title="API Gateway")

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações
LOAD_BALANCER_URL = os.getenv("LOAD_BALANCER_URL", "http://load_balancer:8001")

@app.get("/health")
async def health_check():
    """Endpoint para verificar a saúde do API Gateway"""
    return {"status": "healthy"}

@app.get("/api/users/")
async def list_users():
    """Lista todos os usuários"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{LOAD_BALANCER_URL}/api/users/")
        return response.json()

@app.post("/api/users/")
async def create_user(user: dict, response: Response):
    """Cria um novo usuário"""
    async with httpx.AsyncClient() as client:
        backend_response = await client.post(f"{LOAD_BALANCER_URL}/api/users/", json=user)
        response.status_code = backend_response.status_code
        return backend_response.json()

@app.post("/token")
async def login(username: str, password: str):
    """Endpoint para autenticação"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{LOAD_BALANCER_URL}/token",
            data={"username": username, "password": password}
        )
        return response.json()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 