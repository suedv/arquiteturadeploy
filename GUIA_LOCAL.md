# 🚀 Guia para Rodar o Projeto Localmente

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- ✅ **Python 3.8+**
- ✅ **PostgreSQL**
- ✅ **Git**

## 🎯 Método Rápido (Recomendado)

### 1. **Rodar todos os serviços de uma vez**
```bash
./run_local.sh
```

### 2. **Parar todos os serviços**
```bash
./stop_local.sh
```

---

## 🔧 Método Manual (Passo a Passo)

### **Passo 1: Preparação**
```bash
# Certifique-se de estar na pasta raiz
cd /Users/sued/arquitetura

# Verifique se as pastas existem
ls -la
```

### **Passo 2: Limpar portas ocupadas**
```bash
# Verificar processos nas portas
lsof -i :8000
lsof -i :8001
lsof -i :8002

# Matar processos se necessário
kill -9 <PID>
```

### **Passo 3: Limpar banco de dados (se necessário)**
```bash
# Conectar ao PostgreSQL
psql -U postgres -d arquitetura

# No PostgreSQL, execute:
DROP TABLE IF EXISTS itens CASCADE;
\q
```

### **Passo 4: Rodar o Server (Backend)**
```bash
# Terminal 1
cd server
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8002
```

### **Passo 5: Rodar o Load Balancer**
```bash
# Terminal 2
cd load_balancer
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8001
```

### **Passo 6: Rodar o API Gateway**
```bash
# Terminal 3
cd api_gateway
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🧪 Testando o Sistema

### **1. Verificar se os serviços estão rodando**
```bash
# Teste cada serviço
curl http://localhost:8002/saude  # Server
curl http://localhost:8001/saude  # Load Balancer
curl http://localhost:8000/saude  # API Gateway
```

### **2. Acessar a documentação**
- **Server Docs**: http://localhost:8002/docs
- **Load Balancer Docs**: http://localhost:8001/docs
- **API Gateway Docs**: http://localhost:8000/docs

### **3. Testar o fluxo completo**
```bash
# Fazer uma requisição através do API Gateway
curl http://localhost:8000/itens

# Criar um item
curl -X POST http://localhost:8000/itens \
  -H "Content-Type: application/json" \
  -d '{"nome": "Teste", "descricao": "Item de teste", "preco": 10.50}'
```

---

## 🛠️ Solução de Problemas

### **Erro: "Porta já em uso"**
```bash
# Encontrar o processo
lsof -i :8000

# Matar o processo
kill -9 <PID>
```

### **Erro: "Ambiente virtual não encontrado"**
```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### **Erro: "Banco de dados não conecta"**
```bash
# Verificar se o PostgreSQL está rodando
brew services list | grep postgresql

# Iniciar se necessário
brew services start postgresql
```

### **Erro: "UniqueViolation" no banco**
```bash
# Limpar o banco
psql -U postgres -d arquitetura -c "DROP TABLE IF EXISTS itens CASCADE;"
```

---

## 📊 URLs dos Serviços

| Serviço | URL | Documentação |
|---------|-----|--------------|
| API Gateway | http://localhost:8000 | http://localhost:8000/docs |
| Load Balancer | http://localhost:8001 | http://localhost:8001/docs |
| Server | http://localhost:8002 | http://localhost:8002/docs |

---

## 🔄 Comandos Úteis

### **Verificar status dos serviços**
```bash
# Verificar processos rodando
ps aux | grep uvicorn

# Verificar portas em uso
lsof -i :8000-8002
```

### **Logs em tempo real**
```bash
# Ver logs de todos os serviços
tail -f server/logs/*.log 2>/dev/null || echo "Logs não encontrados"
```

### **Reiniciar um serviço específico**
```bash
# Parar um serviço específico
kill -9 $(lsof -ti:8002)  # Para o server

# Rodar novamente
cd server && source venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8002
```

---

## 🎯 Ordem de Inicialização

1. **Server** (porta 8002) - Backend com banco de dados
2. **Load Balancer** (porta 8001) - Distribui requisições
3. **API Gateway** (porta 8000) - Ponto de entrada da aplicação

---

## 💡 Dicas

- **Use o script automático** (`./run_local.sh`) para facilitar o processo
- **Mantenha 3 terminais abertos** se rodar manualmente
- **Verifique os logs** se algo não funcionar
- **Teste cada serviço individualmente** antes de testar o fluxo completo

---

## 🆘 Ainda com problemas?

1. **Verifique se está na pasta correta**: `/Users/sued/arquitetura`
2. **Confirme se o PostgreSQL está rodando**
3. **Verifique se as variáveis de ambiente estão corretas**
4. **Limpe o banco de dados se necessário**
5. **Reinicie todos os serviços**

Se ainda tiver problemas, verifique os logs de cada serviço para identificar o erro específico. 