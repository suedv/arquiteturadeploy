# Sistema Distribuído com API Gateway

## Diagrama da Arquitetura

```mermaid
graph TD
    Client[Cliente] --> |Requisição| Gateway[API Gateway]
    Gateway --> |Balanceamento| LB[Load Balancer]
    LB --> |Distribuição| Server1[Servidor 1]
    LB --> |Distribuição| Server2[Servidor 2]
    Server1 --> |Persistência| DB[(Banco de Dados)]
    Server2 --> |Persistência| DB
    DB --> |Resposta| Server1
    DB --> |Resposta| Server2
    Server1 --> |Resposta| LB
    Server2 --> |Resposta| LB
    LB --> |Resposta| Gateway
    Gateway --> |Resposta| Client
```

## Padrão MVC

O projeto implementa o padrão MVC (Model-View-Controller) da seguinte forma:

### Model
- Responsável pela lógica de negócios
- Implementa a camada de persistência
- Contém as classes de domínio

### View
- Responsável pela apresentação dos dados
- Serialização em JSON
- Formatação das respostas HTTP

### Controller
- Gerencia as requisições HTTP
- Coordena Model e View
- Implementa as rotas da API

## Instruções de Uso

1. Clone o repositório
2. Configure as variáveis de ambiente:
   ```
   GATEWAY_URL=http://localhost:8000
   LOAD_BALANCER_URL=http://localhost:8001
   SERVER_URL=http://localhost:8002
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   ```
3. Execute com Docker Compose:
   ```bash
   docker-compose up -d
   ```

## Postman Collection

1. Importe o arquivo `postman_collection.json`
2. Configure o ambiente com as variáveis:
   - `gateway_url`
   - `server_url`
3. Execute os testes na ordem:
   - Autenticação
   - CRUD de recursos
   - Cenários de erro

## Responsabilidades Individuais

| Integrante | Componente |
|------------|------------|
| [Nome] | API Gateway |
| [Nome] | Balanceador de Carga |
| [Nome] | Serviço SERVER1 |
| [Nome] | Banco de Dados / Model / DAO |

## URLs de Produção (Railway)

- API Gateway: [URL_DO_GATEWAY]
- Serviço de Aplicação: [URL_DO_SERVICO]

## Convenções de Commit

- feat(componente): nova funcionalidade
- fix(componente): correção de bug
- docs(componente): documentação
- refactor(componente): refatoração

Exemplo: `feat(controller): adiciona rota POST /orders` 