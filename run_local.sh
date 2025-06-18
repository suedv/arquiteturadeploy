#!/bin/bash

echo "🚀 Iniciando Arquitetura Distribuída Localmente"
echo "================================================"

# Função para matar processos em portas específicas
kill_port() {
    local port=$1
    echo "🔍 Verificando porta $port..."
    lsof -ti:$port | xargs kill -9 2>/dev/null || echo "Porta $port livre"
}

# Função para limpar o banco de dados
clean_database() {
    echo "🧹 Limpando banco de dados..."
    psql -U postgres -d arquitetura -c "DROP TABLE IF EXISTS itens CASCADE;" 2>/dev/null || echo "Erro ao limpar banco (pode ignorar se for primeira execução)"
}

# Matar processos nas portas que vamos usar
echo "🛑 Liberando portas..."
kill_port 8000
kill_port 8001
kill_port 8002
kill_port 8003

# Limpar banco de dados
clean_database

echo ""
echo "📁 Verificando estrutura do projeto..."
if [ ! -d "server" ] || [ ! -d "load_balancer" ] || [ ! -d "api_gateway" ]; then
    echo "❌ Estrutura de pastas incorreta!"
    echo "Certifique-se de estar na pasta raiz do projeto (/Users/sued/arquitetura)"
    exit 1
fi

echo "✅ Estrutura OK!"

# Função para rodar um serviço
run_service() {
    local service_name=$1
    local port=$2
    local folder=$3
    
    echo ""
    echo "🔄 Iniciando $service_name na porta $port..."
    
    # Verificar se a pasta existe
    if [ ! -d "$folder" ]; then
        echo "❌ Pasta $folder não encontrada!"
        return 1
    fi
    
    # Entrar na pasta e rodar o serviço
    cd "$folder"
    
    # Verificar se o ambiente virtual existe
    if [ ! -d "venv" ]; then
        echo "📦 Criando ambiente virtual para $service_name..."
        python3 -m venv venv
    fi
    
    # Ativar ambiente virtual
    source venv/bin/activate
    
    # Instalar dependências se necessário
    if [ ! -f "venv/lib/python*/site-packages/fastapi" ]; then
        echo "📥 Instalando dependências para $service_name..."
        pip install -r requirements.txt
    fi
    
    # Rodar o serviço em background
    echo "🚀 Rodando $service_name..."
    uvicorn main:app --host 0.0.0.0 --port $port &
    
    # Voltar para a pasta raiz
    cd ..
    
    # Aguardar um pouco para o serviço inicializar
    sleep 3
    
    # Verificar se o serviço está rodando
    if curl -s http://localhost:$port/saude > /dev/null 2>&1; then
        echo "✅ $service_name rodando em http://localhost:$port"
    else
        echo "⚠️  $service_name pode não estar respondendo ainda"
    fi
}

# Rodar os serviços na ordem correta
echo ""
echo "🎯 Iniciando serviços..."

# 1. Server (Backend)
run_service "Server" 8002 "server"

# 2. Load Balancer
run_service "Load Balancer" 8001 "load_balancer"

# 3. API Gateway
run_service "API Gateway" 8000 "api_gateway"

echo ""
echo "🎉 Todos os serviços iniciados!"
echo ""
echo "📋 URLs dos serviços:"
echo "   • API Gateway: http://localhost:8000"
echo "   • Load Balancer: http://localhost:8001"
echo "   • Server: http://localhost:8002"
echo ""
echo "📚 Documentação:"
echo "   • API Gateway Docs: http://localhost:8000/docs"
echo "   • Load Balancer Docs: http://localhost:8001/docs"
echo "   • Server Docs: http://localhost:8002/docs"
echo ""
echo "🧪 Teste o sistema:"
echo "   curl http://localhost:8000/saude"
echo ""
echo "🛑 Para parar todos os serviços, pressione Ctrl+C"
echo ""

# Manter o script rodando para mostrar logs
wait 