#!/bin/bash

echo "🛑 Parando todos os serviços da Arquitetura Distribuída"
echo "========================================================"

# Função para matar processos em portas específicas
kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port)
    if [ ! -z "$pids" ]; then
        echo "🔍 Parando processo na porta $port (PIDs: $pids)"
        echo $pids | xargs kill -9
        echo "✅ Processo na porta $port parado"
    else
        echo "ℹ️  Nenhum processo rodando na porta $port"
    fi
}

# Parar todos os serviços
echo "🛑 Parando serviços..."
kill_port 8000  # API Gateway
kill_port 8001  # Load Balancer
kill_port 8002  # Server
kill_port 8003  # Server alternativo

echo ""
echo "🎉 Todos os serviços parados!"
echo ""
echo "💡 Para iniciar novamente, execute:"
echo "   ./run_local.sh" 