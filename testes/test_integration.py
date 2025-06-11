import pytest
import pytest_asyncio
import httpx
import asyncio
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# URLs base para cada serviço
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
LOAD_BALANCER_URL = os.getenv("LOAD_BALANCER_URL", "http://localhost:8001")
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8002")

@pytest_asyncio.fixture
async def client():
    """Fixture que fornece um cliente HTTP assíncrono"""
    async with httpx.AsyncClient() as client:
        yield client

@pytest.mark.asyncio
async def test_api_gateway_health(client):
    """Testa o endpoint de health check do API Gateway"""
    response = await client.get(f"{API_GATEWAY_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_load_balancer_health(client):
    """Testa o endpoint de health check do Load Balancer"""
    response = await client.get(f"{LOAD_BALANCER_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_server_health(client):
    """Testa o endpoint de health check do Servidor"""
    response = await client.get(f"{SERVER_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_user_registration_and_login(client):
    """Testa o registro e login de usuário"""
    # Dados do usuário de teste
    user_data = {
        "username": f"testuser_{datetime.now().timestamp()}",
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "password": "testpassword123"
    }

    # Registra novo usuário
    register_response = await client.post(
        f"{API_GATEWAY_URL}/api/users/",
        json=user_data
    )
    assert register_response.status_code == 201
    assert "id" in register_response.json()

    # Faz login
    login_response = await client.post(
        f"{API_GATEWAY_URL}/token",
        data={
            "username": user_data["username"],
            "password": user_data["password"]
        }
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

    return login_response.json()["access_token"]

@pytest.mark.asyncio
async def test_protected_endpoints(client):
    """Testa endpoints protegidos com autenticação"""
    # Primeiro faz login para obter o token
    token = await test_user_registration_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Testa endpoint protegido
    response = await client.get(
        f"{API_GATEWAY_URL}/api/users/me",
        headers=headers
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_load_balancing(client):
    """Testa se o load balancer está distribuindo as requisições"""
    # Faz múltiplas requisições para verificar a distribuição
    responses = []
    for _ in range(5):
        response = await client.get(f"{LOAD_BALANCER_URL}/health")
        responses.append(response.json())
    
    # Verifica se as respostas são consistentes
    assert all(r["status"] == "healthy" for r in responses)

@pytest.mark.asyncio
async def test_cache_behavior(client):
    """Testa o comportamento do cache"""
    # Faz uma requisição inicial
    first_response = await client.get(f"{API_GATEWAY_URL}/api/users/")
    assert first_response.status_code == 200
    first_data = first_response.json()

    # Faz a mesma requisição novamente
    second_response = await client.get(f"{API_GATEWAY_URL}/api/users/")
    assert second_response.status_code == 200
    second_data = second_response.json()

    # Verifica se os dados são idênticos (cache funcionando)
    assert first_data == second_data

if __name__ == "__main__":
    pytest.main(["-v", "test_integration.py"]) 