#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "🚀 Iniciando testes da aplicação..."

# Verifica se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 não está instalado. Por favor, instale o Python3 primeiro.${NC}"
    exit 1
fi

# Verifica se o pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 não está instalado. Por favor, instale o pip3 primeiro.${NC}"
    exit 1
fi

# Instala as dependências de teste
echo "📦 Instalando dependências de teste..."
pip3 install -r requirements.txt

# Verifica se o Docker está instalado e rodando
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker não está instalado. Por favor, instale o Docker primeiro.${NC}"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker não está rodando. Por favor, inicie o Docker primeiro.${NC}"
    exit 1
fi

# Inicia os serviços necessários usando Docker Compose
echo "🐳 Iniciando serviços com Docker Compose..."
docker-compose down && docker-compose build --no-cache server1 server2 && docker-compose up -d

# Aguarda os serviços iniciarem
echo "⏳ Aguardando serviços iniciarem..."
sleep 10

# Executa os testes
echo "🧪 Executando testes..."
python3 -m pytest test_integration.py -v

# Captura o resultado dos testes
TEST_RESULT=$?

# Para os serviços
echo "🛑 Parando serviços..."
docker-compose down

# Verifica o resultado dos testes
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Todos os testes passaram com sucesso!${NC}"
else
    echo -e "${RED}❌ Alguns testes falharam. Por favor, verifique os logs acima.${NC}"
fi

exit $TEST_RESULT 