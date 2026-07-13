# Alpha Gestão API

API backend do **Alpha Gestão**, uma aplicação de gestão financeira pessoal para importação de faturas, organização de transações, autenticação de usuários e geração de análises financeiras.

---

## 1. O que o projeto faz

A API do Alpha Gestão centraliza as regras de negócio da aplicação financeira.

Principais funcionalidades:

- autenticação de usuários com JWT;
- cadastro de novos usuários;
- aceite obrigatório de Termos de Uso e Aviso de Privacidade no cadastro;
- importação de faturas por arquivo;
- extração e persistência de transações;
- listagem e detalhamento de faturas;
- exclusão de faturas e suas transações vinculadas;
- cadastro manual de transações;
- edição e exclusão de transações;
- filtros por cartão, categoria, tipo e período;
- geração de dados analíticos para o dashboard;
- identificação de padrões de consumo e insights financeiros.

A API foi construída para servir o frontend Angular do Alpha Gestão, mas também pode ser consumida diretamente por ferramentas como Swagger, Postman, Insomnia ou qualquer cliente HTTP.

---

## 2. Tecnologias utilizadas

Principais tecnologias do backend:

- **Python**
- **FastAPI**
- **SQLAlchemy**
- **SQLite**
- **Pydantic**
- **JWT**
- **PyJWT**
- **pwdlib[argon2]**
- **Uvicorn**
- **python-multipart**
- **email-validator**

Finalidade das principais dependências:

| Tecnologia | Uso |
|---|---|
| FastAPI | Criação da API REST |
| SQLAlchemy | ORM e comunicação com o banco |
| SQLite | Banco de dados local |
| Pydantic | Validação e serialização de dados |
| JWT | Autenticação por token |
| pwdlib[argon2] | Hash seguro de senhas |
| Uvicorn | Servidor ASGI |
| python-multipart | Upload de arquivos |
| email-validator | Validação de e-mails |

---

## 3. Requisitos

Antes de executar o projeto, verifique se possui:

- Python 3.11 ou superior;
- pip instalado;
- ambiente virtual configurado;
- Git instalado, caso deseje clonar o repositório.

---

## 4. Como instalar e executar

### 4.1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd alpha-api
```

### 4.2. Criar ambiente virtual

No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

No Windows CMD:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

No Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4.3. Instalar dependências

```bash
pip install -r requirements.txt
```

Caso o arquivo `requirements.txt` ainda não exista, instale as dependências principais:

```bash
pip install fastapi uvicorn sqlalchemy pydantic pyjwt "pwdlib[argon2]" python-multipart email-validator
```

### 4.4. Executar a API

```bash
uvicorn app.main:app --reload
```

Após iniciar, a API estará disponível em:

```text
http://127.0.0.1:8000
```

Documentação interativa do Swagger:

```text
http://127.0.0.1:8000/docs
```

Documentação ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

## 5. Configuração de variáveis de ambiente

A API utiliza variáveis de ambiente para configurar informações sensíveis e parâmetros da aplicação.

### 5.1. Variáveis recomendadas

Crie um arquivo `.env` na raiz do projeto:

```env
JWT_SECRET_KEY=altere-esta-chave-em-producao
DATABASE_URL=sqlite:///./alpha.db
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

### 5.2. Descrição das variáveis

| Variável | Obrigatória | Descrição |
|---|---:|---|
| JWT_SECRET_KEY | Sim em produção | Chave usada para assinar os tokens JWT |
| DATABASE_URL | Não | URL de conexão com o banco de dados |
| ACCESS_TOKEN_EXPIRE_MINUTES | Não | Tempo de expiração do token em minutos |

### 5.3. Observação importante

Em ambiente de desenvolvimento, a aplicação pode usar valores padrão definidos no código.

Em produção, nunca utilize a chave padrão. Configure uma chave forte e privada em `JWT_SECRET_KEY`.

Exemplo de chave forte:

```text
JWT_SECRET_KEY=uma-chave-longa-aleatoria-e-secreta
```

---

## 6. Exemplos básicos de uso

Os exemplos abaixo usam o prefixo padrão:

```text
/api/v1
```

### 6.1. Cadastro de usuário

Endpoint:

```http
POST /api/v1/auth/register
```

Exemplo de requisição:

```json
{
  "name": "Usuário Teste",
  "email": "teste@alphagestao.com",
  "password": "senha1234",
  "password_confirmation": "senha1234",
  "privacy_acceptance": true
}
```

Exemplo de resposta:

```json
{
  "id": 1,
  "name": "Usuário Teste",
  "email": "teste@alphagestao.com",
  "message": "Usuário criado com sucesso."
}
```

O campo `privacy_acceptance` é obrigatório. O cadastro não deve ser concluído quando o usuário não aceitar os Termos de Uso e declarar ciência do Aviso de Privacidade.

---

### 6.2. Login

Endpoint:

```http
POST /api/v1/auth/login
```

Exemplo de requisição:

```json
{
  "email": "teste@alphagestao.com",
  "password": "senha1234"
}
```

Exemplo de resposta:

```json
{
  "access_token": "token-jwt-gerado-pela-api",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Usuário Teste",
    "email": "teste@alphagestao.com"
  }
}
```

---

### 6.3. Consultar usuário autenticado

Endpoint:

```http
GET /api/v1/auth/me
```

Header obrigatório:

```http
Authorization: Bearer <access_token>
```

Exemplo de resposta:

```json
{
  "id": 1,
  "name": "Usuário Teste",
  "email": "teste@alphagestao.com"
}
```

---

### 6.4. Importar fatura

Endpoint:

```http
POST /api/v1/invoices/import
```

Tipo de envio:

```text
multipart/form-data
```

Campo esperado:

```text
file
```

Exemplo usando cURL:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/invoices/import" \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@fatura.pdf"
```

---

### 6.5. Listar faturas

Endpoint:

```http
GET /api/v1/invoices
```

Header obrigatório:

```http
Authorization: Bearer <access_token>
```

Exemplo de resposta:

```json
[
  {
    "id": 1,
    "filename": "fatura.pdf",
    "total_amount": 1504.08,
    "total_transactions": 50
  }
]
```

---

### 6.6. Buscar detalhes de uma fatura

Endpoint:

```http
GET /api/v1/invoices/{invoice_id}
```

Exemplo:

```http
GET /api/v1/invoices/1
```

---

### 6.7. Excluir fatura

Endpoint:

```http
DELETE /api/v1/invoices/{invoice_id}
```

Exemplo de resposta:

```json
{
  "message": "Fatura excluída com sucesso.",
  "invoice_id": 1,
  "deleted_transactions": 50
}
```

---

### 6.8. Filtrar transações

Endpoint:

```http
GET /api/v1/transactions/filter
```

Parâmetros aceitos:

| Parâmetro | Tipo | Descrição |
|---|---|---|
| invoice_id | int | Filtra por fatura |
| card | string | Filtra por cartão |
| category | string | Filtra por categoria |
| type | string | Filtra por tipo |
| start_date | date | Data inicial |
| end_date | date | Data final |

Exemplo:

```http
GET /api/v1/transactions/filter?category=Alimentação&start_date=2026-07-01&end_date=2026-07-31
```

---

### 6.9. Consultar opções dos filtros

Endpoint:

```http
GET /api/v1/transactions/filter-options
```

Exemplo de resposta:

```json
{
  "cards": ["3825", "4945"],
  "categories": ["Alimentação", "Transporte", "Saúde"],
  "types": ["compra", "estorno", "pagamento", "financiamento"],
  "min_date": "2026-06-01",
  "max_date": "2026-07-31"
}
```

---

### 6.10. Cadastrar transação manual

Endpoint:

```http
POST /api/v1/transactions/manual
```

Exemplo de requisição:

```json
{
  "invoice_id": null,
  "transaction_date": "2026-07-08",
  "card": "3825",
  "description": "Farmácia",
  "amount": 72.5,
  "category": "Saúde"
}
```

---

### 6.11. Editar transação

Endpoint:

```http
PATCH /api/v1/transactions/{transaction_id}
```

Exemplo de requisição:

```json
{
  "description": "Farmácia Atualizada",
  "amount": 80.0,
  "category": "Saúde"
}
```

---

### 6.12. Excluir transação

Endpoint:

```http
DELETE /api/v1/transactions/{transaction_id}
```

Exemplo de resposta:

```json
{
  "message": "Transação excluída com sucesso.",
  "transaction_id": 10
}
```

---

### 6.13. Consultar dashboard

Endpoint:

```http
GET /api/v1/dashboard
```

Filtros opcionais:

| Parâmetro | Tipo | Descrição |
|---|---|---|
| invoice_id | int | Filtra por fatura |
| card | string | Filtra por cartão |
| category | string | Filtra por categoria |
| start_date | date | Data inicial |
| end_date | date | Data final |

Exemplo:

```http
GET /api/v1/dashboard?card=3825&start_date=2026-07-01&end_date=2026-07-31
```

---

## 7. Estrutura resumida das pastas

Estrutura esperada do projeto:

```text
alpha-api/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── dashboard.py
│   │       ├── faturas.py
│   │       └── transactions.py
│   │
│   ├── core/
│   │   └── security.py
│   │
│   ├── database/
│   │   └── database.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── fatura.py
│   │   ├── transaction.py
│   │   └── user.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── fatura.py
│   │   └── transaction.py
│   │
│   ├── services/
│   │   ├── user_login/
│   │   │   ├── auth_service.py
│   │   │   └── user_repository.py
│   │   │
│   │   ├── date_normalizer.py
│   │   └── demais serviços de negócio
│   │
│   └── main.py
│
├── alpha.db
├── requirements.txt
└── README.md
```

---

## 8. Responsabilidade das principais pastas

### app/api/routes

Contém as rotas HTTP da aplicação.

Cada arquivo agrupa endpoints relacionados a um domínio específico.

Exemplos:
- `auth.py`: login, cadastro e usuário autenticado;
- `faturas.py`: importação, listagem, detalhe e exclusão de faturas;
- `transactions.py`: filtros, cadastro manual, edição e exclusão de transações;
- `dashboard.py`: dados analíticos do dashboard.

### app/core

Contém configurações centrais e utilitários de segurança.

Exemplo:
- geração de hash de senha;
- validação de senha;
- criação e decodificação de JWT.

### app/database

Contém configuração do banco de dados.

Responsabilidades:
- criar engine;
- criar sessão;
- criar tabelas;
- executar ajustes simples de estrutura no SQLite.

### app/models

Contém os modelos SQLAlchemy.

Representa as tabelas do banco.

Principais modelos:
- Usuario;
- Fatura;
- Transacao.

### app/schemas

Contém os schemas Pydantic.

Responsabilidades:
- validar dados de entrada;
- definir formato das respostas;
- documentar contratos da API.

### app/services

Contém regras de negócio, consultas e operações auxiliares.

A ideia é manter as rotas enxutas e concentrar a lógica fora da camada HTTP.

---

## 9. Autenticação e segurança

A API utiliza autenticação via JWT.

Fluxo básico:

1. Usuário realiza login.
2. API valida e-mail e senha.
3. API retorna um token JWT.
4. Cliente envia o token no header Authorization.
5. Rotas privadas validam o token antes de executar a ação.

Formato do header:

```http
Authorization: Bearer <access_token>
```

As senhas são armazenadas com hash, nunca em texto puro.

---

## 10. Status atual do projeto

Implementado:

- autenticação com JWT;
- cadastro de usuários;
- aceite obrigatório de privacidade no cadastro;
- importação de faturas;
- listagem e detalhe de faturas;
- exclusão de faturas;
- cadastro manual de transações;
- filtros de transações;
- edição e exclusão de transações;
- dashboard analítico;
- endpoints protegidos por autenticação.

Pendente ou recomendado:

- isolamento completo de dados por usuário;
- criação de páginas reais de Termos de Uso e Aviso de Privacidade;
- testes automatizados;
- migração formal com Alembic;
- configuração de banco de produção;
- deploy com variáveis de ambiente seguras.

---

## 11. Boas práticas adotadas

- Separação entre rotas, services, schemas e models.
- Uso de schemas Pydantic para entrada e saída.
- Uso de JWT para autenticação.
- Hash seguro de senhas.
- Endpoints organizados por domínio.
- Prefixo versionado `/api/v1`.
- Tratamento de erros HTTP com mensagens claras.
- Validação de aceite de privacidade no frontend e no backend.

---

## 12. Comandos úteis

Executar a API:

```bash
uvicorn app.main:app --reload
```

Instalar dependências:

```bash
pip install -r requirements.txt
```

Gerar arquivo de dependências:

```bash
pip freeze > requirements.txt
```

Acessar Swagger:

```text
http://127.0.0.1:8000/docs
```

Acessar ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

## 13. Licença

Definir a licença do projeto conforme a estratégia de distribuição.

Exemplos comuns:
- MIT;
- Apache 2.0;
- Proprietária.

---

## 14. Autor

Projeto desenvolvido como backend da aplicação Alpha Gestão.
