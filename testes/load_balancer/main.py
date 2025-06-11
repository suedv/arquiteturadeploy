from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from typing import List
import random

app = FastAPI(title="Load Balancer")

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações
SERVER_URLS = [
    os.getenv("SERVER1_URL", "http://server1:8002"),
    os.getenv("SERVER2_URL", "http://server2:8003")
]

@app.get("/health")
async def health_check():
    """Endpoint para verificar a saúde do Load Balancer"""
    return {"status": "healthy"}

@app.get("/api/users/")
async def list_users():
    """Lista todos os usuários"""
    server_url = random.choice(SERVER_URLS)
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{server_url}/api/users/")
        return response.json()

@app.post("/api/users/")
async def create_user(user: dict, response: Response):
    """Cria um novo usuário"""
    server_url = random.choice(SERVER_URLS)
    async with httpx.AsyncClient() as client:
        backend_response = await client.post(f"{server_url}/api/users/", json=user)
        response.status_code = backend_response.status_code
        return backend_response.json()

@app.post("/token")
async def login(username: str, password: str):
    """Endpoint para autenticação"""
    server_url = random.choice(SERVER_URLS)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{server_url}/token",
            data={"username": username, "password": password}
        )
        return response.json()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 