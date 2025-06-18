#!/bin/bash

echo "🚀 Teste rápido da arquitetura..."

# Parar processos existentes
echo "🛑 Parando processos existentes..."
pkill -f "uvicorn main:app" 2>/dev/null
sleep 2

# Verificar se o PostgreSQL está rodando
echo "🔍 Verificando PostgreSQL..."
if ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    echo "❌ PostgreSQL não está rodando. Inicie o PostgreSQL primeiro."
    exit 1
fi
echo "✅ PostgreSQL está rodando"

# Criar banco se não existir
echo "🗄️ Verificando banco de dados..."
createdb -h localhost arquitetura 2>/dev/null || echo "Banco já existe"

# Instalar PyJWT no API Gateway
echo "📦 Instalando PyJWT..."
cd api_gateway
source venv/bin/activate
pip install PyJWT==2.8.0
cd ..

# Iniciar servidores
echo "🚀 Iniciando servidores..."

# Server 1
cd server
source venv/bin/activate
export DATABASE_URL="postgresql://sued@localhost:5432/arquitetura"
export PORTA=8002
uvicorn main:app --host 0.0.0.0 --port 8002 &
echo "✅ Server 1 iniciado na porta 8002"
cd ..

# Server 2
cd server2
source venv/bin/activate
export DATABASE_URL="postgresql://sued@localhost:5432/arquitetura"
export PORTA=8003
uvicorn main:app --host 0.0.0.0 --port 8003 &
echo "✅ Server 2 iniciado na porta 8003"
cd ..

sleep 3

# Load Balancer
cd load_balancer
source venv/bin/activate
export SERVIDORES="http://localhost:8002,http://localhost:8003"
uvicorn main:app --host 0.0.0.0 --port 8001 &
echo "✅ Load Balancer iniciado na porta 8001"
cd ..

sleep 2

# API Gateway
cd api_gateway
source venv/bin/activate
export LOAD_BALANCER_URL="http://localhost:8001"
export SECRET_KEY="sua_chave_secreta_aqui"
uvicorn main:app --host 0.0.0.0 --port 8000 &
echo "✅ API Gateway iniciado na porta 8000"
cd ..

sleep 3

echo ""
echo "🎉 Arquitetura iniciada!"
echo ""
echo "📋 Endpoints:"
echo "   API Gateway: http://localhost:8000"
echo "   Load Balancer: http://localhost:8001"
echo "   Server 1: http://localhost:8002"
echo "   Server 2: http://localhost:8003"
echo ""
echo "🔧 Teste rápido:"
echo "   curl http://localhost:8000/saude"
echo "   curl http://localhost:8001/saude"
echo "   curl http://localhost:8002/saude"
echo "   curl http://localhost:8003/saude"
echo ""
echo "🛑 Para parar: pkill -f 'uvicorn main:app'" 