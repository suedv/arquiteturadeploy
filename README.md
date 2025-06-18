# 🏗️ Arquitetura Distribuída - FastAPI

Uma arquitetura distribuída completa com FastAPI, incluindo API Gateway, Load Balancer, múltiplos servidores, cache, monitoramento e autenticação JWT.

## 📋 Componentes da Arquitetura

### 🔐 API Gateway (Porta 8000)
- **Função**: Ponto de entrada único para todas as requisições
- **Funcionalidades**:
  - Autenticação JWT
  - Rate limiting
  - Roteamento para Load Balancer
  - Documentação Swagger
- **Endpoints**:
  - `POST /login` - Autenticação
  - `POST /register` - Registro de usuários
  - `GET /saude` - Health check
  - `GET /docs` - Documentação

### ⚖️ Load Balancer (Porta 8001)
- **Função**: Distribui carga entre múltiplos servidores
- **Algoritmo**: Round-robin
- **Funcionalidades**:
  - Balanceamento automático
  - Health checks
  - Logs de requisições
- **Endpoints**:
  - `GET /saude` - Health check

### 🖥️ Servidores de Aplicação (Portas 8002, 8003)
- **Função**: Processam requisições de negócio
- **Tecnologias**: FastAPI + SQLAlchemy + PostgreSQL
- **Funcionalidades**:
  - CRUD completo de itens
  - Validação de dados
  - Respostas padronizadas
- **Endpoints**:
  - `GET /saude` - Health check
  - `GET /itens` - Listar itens
  - `POST /itens` - Criar item
  - `GET /itens/{id}` - Buscar item
  - `PUT /itens/{id}` - Atualizar item
  - `DELETE /itens/{id}` - Deletar item

### 🗄️ Cache (Porta 8004)
- **Função**: Cache Redis para melhorar performance
- **Funcionalidades**:
  - Cache de dados
  - Estatísticas de uso
  - TTL configurável
- **Endpoints**:
  - `GET /cache/{key}` - Buscar no cache
  - `POST /cache` - Armazenar no cache
  - `DELETE /cache/{key}` - Remover do cache
  - `GET /cache/stats` - Estatísticas

### 📊 Monitoramento (Porta 8005)
- **Função**: Monitoramento e alertas
- **Funcionalidades**:
  - Health checks dos serviços
  - Métricas de performance
  - Alertas automáticos
  - Dashboard
- **Endpoints**:
  - `GET /health` - Status dos serviços
  - `GET /metrics` - Métricas
  - `GET /alerts` - Alertas ativos
  - `GET /dashboard` - Dashboard

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.11+
- PostgreSQL
- Redis (opcional)
- Docker (opcional)

### 1. Configurar Banco de Dados
```bash
# Criar banco PostgreSQL
createdb arquitetura

# Ou usar Docker
docker run --name postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=arquitetura -p 5432:5432 -d postgres:15
```

### 2. Instalar Dependências
```bash
# Para cada serviço
cd api_gateway && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cd ../load_balancer && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cd ../server && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cd ../server2 && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cd ../cache && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cd ../monitoring && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

### 3. Iniciar Serviços

#### Opção 1: Script Automático (Recomendado)
```bash
# Teste rápido
./quick_test.sh

# Ou teste completo
./test_architecture.sh
```

#### Opção 2: Manual
```bash
# Terminal 1 - Server 1
cd server
source venv/bin/activate
export DATABASE_URL="postgresql://sued@localhost:5432/arquitetura"
export PORTA=8002
uvicorn main:app --host 0.0.0.0 --port 8002

# Terminal 2 - Server 2
cd server2
source venv/bin/activate
export DATABASE_URL="postgresql://sued@localhost:5432/arquitetura"
export PORTA=8003
uvicorn main:app --host 0.0.0.0 --port 8003

# Terminal 3 - Load Balancer
cd load_balancer
source venv/bin/activate
export SERVIDORES="http://localhost:8002,http://localhost:8003"
uvicorn main:app --host 0.0.0.0 --port 8001

# Terminal 4 - API Gateway
cd api_gateway
source venv/bin/activate
export LOAD_BALANCER_URL="http://localhost:8001"
export SECRET_KEY="sua_chave_secreta_aqui"
uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 5 - Cache (opcional)
cd cache
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8004

# Terminal 6 - Monitoramento (opcional)
cd monitoring
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8005
```

## 🧪 Testes

### Teste Automático
```bash
# Executar todos os testes
python test_endpoints.py
```

### Teste Manual
```bash
# 1. Verificar saúde dos serviços
curl http://localhost:8000/saude
curl http://localhost:8001/saude
curl http://localhost:8002/saude
curl http://localhost:8003/saude

# 2. Fazer login
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 3. Usar o token retornado para acessar itens
curl -X GET http://localhost:8000/itens \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"

# 4. Criar um item
curl -X POST http://localhost:8000/itens \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Item Teste", "descricao": "Descrição", "preco": 99.99}'
```

## 🔧 Configuração

### Variáveis de Ambiente

#### API Gateway
```bash
LOAD_BALANCER_URL=http://localhost:8001
SECRET_KEY=sua_chave_secreta_aqui
```

#### Load Balancer
```bash
SERVIDORES=http://localhost:8002,http://localhost:8003
```

#### Servers
```bash
DATABASE_URL=postgresql://sued@localhost:5432/arquitetura
PORTA=8002  # ou 8003 para o segundo servidor
```

#### Cache
```bash
REDIS_URL=redis://localhost:6379
```

## 📊 Monitoramento

### Health Checks
- API Gateway: `http://localhost:8000/saude`
- Load Balancer: `http://localhost:8001/saude`
- Server 1: `http://localhost:8002/saude`
- Server 2: `http://localhost:8003/saude`
- Cache: `http://localhost:8004/saude`
- Monitoramento: `http://localhost:8005/health`

### Logs
Todos os serviços geram logs detalhados incluindo:
- Requisições recebidas
- Erros e exceções
- Métricas de performance
- Balanceamento de carga

## 🐳 Docker

### Usar Docker Compose
```bash
# Iniciar toda a arquitetura
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar
docker-compose down
```

### Build Individual
```bash
# Para cada serviço
cd api_gateway && docker build -t api-gateway .
cd ../load_balancer && docker build -t load-balancer .
cd ../server && docker build -t server .
cd ../server2 && docker build -t server2 .
cd ../cache && docker build -t cache .
cd ../monitoring && docker build -t monitoring .
```

## 🔄 CI/CD

O projeto inclui GitHub Actions para:
- Testes automáticos
- Linting
- Deploy automático no Railway
- Build de Docker images

## 🛠️ Troubleshooting

### Problemas Comuns

#### 1. Porta já em uso
```bash
# Verificar processos
lsof -i :8000
lsof -i :8001
lsof -i :8002
lsof -i :8003

# Matar processos
pkill -f "uvicorn main:app"
```

#### 2. Erro de banco de dados
```bash
# Verificar se PostgreSQL está rodando
pg_isready -h localhost -p 5432

# Recriar banco
dropdb arquitetura
createdb arquitetura
```

#### 3. Erro de módulo JWT
```bash
# Instalar PyJWT
cd api_gateway
source venv/bin/activate
pip install PyJWT==2.8.0
```

#### 4. Erro de serialização
Os problemas de serialização foram corrigidos nos arquivos:
- `server/main.py`
- `load_balancer/main.py`
- `api_gateway/main.py`

### Logs de Debug
```bash
# Ver logs detalhados
tail -f server/logs/app.log
tail -f load_balancer/logs/app.log
tail -f api_gateway/logs/app.log
```

## 📈 Performance

### Métricas Esperadas
- **Latência**: < 100ms para requisições simples
- **Throughput**: 1000+ req/s com balanceamento
- **Disponibilidade**: 99.9% com múltiplos servidores
- **Cache Hit Rate**: > 80% com Redis

### Otimizações
- Connection pooling no banco
- Cache Redis para dados frequentes
- Load balancing round-robin
- Compressão gzip
- CORS configurado

## 🔒 Segurança

### Autenticação
- JWT tokens com expiração
- Senhas hasheadas com SHA256
- Middleware de autenticação
- Rate limiting

### Usuários Padrão
- **admin/admin123** - Administrador
- **user/user123** - Usuário comum

## 📚 Documentação

### Swagger UI
- API Gateway: `http://localhost:8000/docs`
- Load Balancer: `http://localhost:8001/docs`
- Server 1: `http://localhost:8002/docs`
- Server 2: `http://localhost:8003/docs`

### Postman Collection
Importe o arquivo `Arquitetura_Distribuida.postman_collection.json` no Postman para testes automatizados.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Para dúvidas ou problemas:
1. Verifique a seção de troubleshooting
2. Consulte os logs dos serviços
3. Execute os testes automáticos
4. Abra uma issue no GitHub

---

**Desenvolvido com ❤️ usando FastAPI, PostgreSQL, Redis e Docker**