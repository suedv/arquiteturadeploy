# Sistema Distribuído com API Gateway e Load Balancer

Este projeto implementa uma arquitetura distribuída com API Gateway, Load Balancer e múltiplos servidores de aplicação, seguindo o padrão MVC.

## Arquitetura

```mermaid
graph LR
    Client[Cliente HTTP/Postman] --> Gateway[API Gateway]
    Gateway --> LB[Load Balancer]
    LB --> Server1[Server 1]
    LB --> Server2[Server 2]
    Server1 --> DB[(PostgreSQL)]
    Server2 --> DB
```

## Padrão MVC

O projeto segue o padrão Model-View-Controller (MVC) em cada serviço:

### Model
- Define as entidades de domínio (ex: Item)
- Encapsula o acesso a dados (SQLAlchemy)
- Implementa regras de negócio e validações

### View
- Representada pelas respostas JSON formatadas
- Estrutura consistente de envelope:
```json
{
    "status": "success",
    "data": { ... },
    "message": null
}
```
ou em caso de erro:
```json
{
    "status": "error",
    "data": null,
    "message": "Mensagem de erro"
}
```

### Controller
- Expõe as rotas REST
- Valida parâmetros
- Orquestra chamadas ao Model
- Retorna a View adequada

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

A coleção Postman (`postman_collection.json`) inclui:

1. **Autenticação**
   - POST /token - Obter token JWT

2. **Operações CRUD**
   - POST /itens - Criar novo item
   - GET /itens - Listar todos os itens
   - GET /itens/{id} - Obter item específico
   - PUT /itens/{id} - Atualizar item
   - DELETE /itens/{id} - Remover item

3. **Testes de Balanceamento**
   - GET /identidade - Verificar qual servidor respondeu

4. **Cenários de Erro**
   - Autenticação inválida
   - Item não encontrado
   - Validação de dados
   - Serviço indisponível

Para usar a coleção:
1. Importe o arquivo `postman_collection.json` no Postman
2. Configure a variável de ambiente `base_url` com a URL do API Gateway
3. Execute a requisição de autenticação e copie o token
4. Configure a variável de ambiente `token` com o valor copiado

## Deploy no Railway

O projeto está disponível em:
- API Gateway: [https://api-gateway.up.railway.app](https://api-gateway.up.railway.app)
- Server 1: [https://server1.up.railway.app](https://server1.up.railway.app)
- Server 2: [https://server2.up.railway.app](https://server2.up.railway.app)

## Responsabilidades Individuais

| Integrante | Componente | Responsabilidades |
|------------|------------|-------------------|
| [Nome] | API Gateway | Autenticação JWT, roteamento, proxy |
| [Nome] | Load Balancer | Balanceamento round-robin, proxy |
| [Nome] | Server 1 | CRUD de itens, modelo MVC |
| [Nome] | Server 2 | CRUD de itens, modelo MVC |
| [Nome] | Banco de Dados | Modelo SQLAlchemy, DAO |

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