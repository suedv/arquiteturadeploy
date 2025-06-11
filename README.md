# Sistema Distribuído com API Gateway e Load Balancer

Este projeto implementa uma arquitetura distribuída com API Gateway, Load Balancer e múltiplos servidores de aplicação, seguindo o padrão MVC.

## Arquitetura

```
┌─────────────┐     ┌───────────────┐     ┌─────────────┐
│             │     │               │     │             │
│  API Gateway│────▶│Load Balancer  │────▶│   Server 1  │
│  (Port 8000)│     │  (Port 8001)  │     │  (Port 8002)│
│             │     │               │     │             │
└─────────────┘     └───────────────┘     └─────────────┘
                           │
                           │
                           ▼
                    ┌─────────────┐
                    │             │
                    │   Server 2  │
                    │  (Port 8003)│
                    │             │
                    └─────────────┘
```

## Requisitos

- Python 3.8+
- PostgreSQL
- pip (gerenciador de pacotes Python)

## Configuração do Ambiente

1. Clone o repositório
2. Crie um ambiente virtual Python para cada serviço:
```bash
# API Gateway
cd api_gateway
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Load Balancer
cd ../load_balancer
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Server
cd ../server
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:

**api_gateway/.env**
```
SECRET_KEY=supersecret
LOAD_BALANCER_URL=http://localhost:8001
```

**load_balancer/.env**
```
SERVIDORES=http://localhost:8002,http://localhost:8003
```

**server/.env**
```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

4. Configure o banco de dados PostgreSQL:
```sql
CREATE DATABASE dbname;
CREATE USER user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE dbname TO user;
```

## Executando os Serviços

1. Inicie o banco de dados PostgreSQL

2. Em terminais separados, execute cada serviço:

```bash
# Terminal 1 - API Gateway
cd api_gateway
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2 - Load Balancer
cd load_balancer
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
uvicorn main:app --host 0.0.0.0 --port 8001

# Terminal 3 - Server 1
cd server
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
uvicorn main:app --host 0.0.0.0 --port 8002

# Terminal 4 - Server 2
cd server
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
uvicorn main:app --host 0.0.0.0 --port 8003
```

## Testando a Aplicação

1. Acesse a documentação Swagger em http://localhost:8000/docs

2. Autenticação:
   - Use o endpoint `/token` com as credenciais:
     - Username: usuario
     - Password: senha123
   - Copie o token retornado

3. Use o token no header de todas as requisições:
   ```
   Authorization: Bearer <seu_token>
   ```

4. Endpoints disponíveis:
   - POST /itens - Criar item
   - GET /itens - Listar itens
   - GET /itens/{id} - Obter item
   - PUT /itens/{id} - Atualizar item
   - DELETE /itens/{id} - Remover item

## Coleção Postman

Uma coleção Postman está disponível no arquivo `postman_collection.json` com exemplos de todas as requisições necessárias.

## Estrutura do Projeto

```
.
├── api_gateway/
│   ├── main.py
│   ├── requirements.txt
│   └── .env
├── load_balancer/
│   ├── main.py
│   ├── requirements.txt
│   └── .env
├── server/
│   ├── main.py
│   ├── requirements.txt
│   └── .env
├── postman_collection.json
└── README.md
```