#!/bin/bash

echo "🚀 Iniciando teste da arquitetura distribuída..."

# Função para verificar se uma porta está em uso
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ Porta $port já está em uso"
        return 1
    else
        echo "✅ Porta $port está livre"
        return 0
    fi
}

# Função para aguardar um serviço ficar disponível
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Aguardando $service_name ficar disponível..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url/saude" > /dev/null 2>&1; then
            echo "✅ $service_name está disponível!"
            return 0
        fi
        
        echo "   Tentativa $attempt/$max_attempts..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name não ficou disponível após $max_attempts tentativas"
    return 1
}

# Verificar portas
echo "🔍 Verificando portas..."
check_port 8000 || exit 1
check_port 8001 || exit 1
check_port 8002 || exit 1
check_port 8003 || exit 1

# Instalar dependências do API Gateway
echo "📦 Instalando dependências do API Gateway..."
cd api_gateway
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Instalar dependências do Load Balancer
echo "📦 Instalando dependências do Load Balancer..."
cd load_balancer
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Instalar dependências dos Servers
echo "📦 Instalando dependências dos Servers..."
cd server
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
cd ..

cd server2
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Iniciar servidores em background
echo "🚀 Iniciando servidores..."

# Server 1
cd server
source venv/bin/activate
export DATABASE_URL="postgresql://sued@localhost:5432/arquitetura"
export PORTA=8002
uvicorn main:app --host 0.0.0.0 --port 8002 &
SERVER1_PID=$!
cd ..

# Server 2
cd server2
source venv/bin/activate
export DATABASE_URL="postgresql://sued@localhost:5432/arquitetura"
export PORTA=8003
uvicorn main:app --host 0.0.0.0 --port 8003 &
SERVER2_PID=$!
cd ..

# Aguardar servidores ficarem disponíveis
wait_for_service "http://localhost:8002" "Server 1" || exit 1
wait_for_service "http://localhost:8003" "Server 2" || exit 1

# Load Balancer
cd load_balancer
source venv/bin/activate
export SERVIDORES="http://localhost:8002,http://localhost:8003"
uvicorn main:app --host 0.0.0.0 --port 8001 &
LOAD_BALANCER_PID=$!
cd ..

wait_for_service "http://localhost:8001" "Load Balancer" || exit 1

# API Gateway
cd api_gateway
source venv/bin/activate
export LOAD_BALANCER_URL="http://localhost:8001"
export SECRET_KEY="sua_chave_secreta_aqui"
uvicorn main:app --host 0.0.0.0 --port 8000 &
GATEWAY_PID=$!
cd ..

wait_for_service "http://localhost:8000" "API Gateway" || exit 1

echo "🎉 Todos os serviços estão rodando!"
echo ""
echo "📋 Endpoints disponíveis:"
echo "   API Gateway: http://localhost:8000"
echo "   Load Balancer: http://localhost:8001"
echo "   Server 1: http://localhost:8002"
echo "   Server 2: http://localhost:8003"
echo ""
echo "🔧 Para testar:"
echo "   1. Acesse http://localhost:8000/docs para ver a documentação"
echo "   2. Faça login: POST http://localhost:8000/login"
echo "   3. Use o token para acessar /itens"
echo ""
echo "🛑 Para parar todos os serviços, pressione Ctrl+C"

# Função para limpar processos ao sair
cleanup() {
    echo ""
    echo "🛑 Parando todos os serviços..."
    kill $SERVER1_PID $SERVER2_PID $LOAD_BALANCER_PID $GATEWAY_PID 2>/dev/null
    echo "✅ Serviços parados"
    exit 0
}

# Capturar Ctrl+C
trap cleanup SIGINT

# Manter o script rodando
wait 