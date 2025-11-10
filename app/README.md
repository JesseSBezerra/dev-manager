# DynamoDB Manager - Flask MVC Application

Aplicação web para gerenciar tabelas DynamoDB na AWS usando Flask com arquitetura MVC.

## 📋 Características

- ✅ Arquitetura MVC (Model-View-Controller)
- ✅ Criação de tabelas DynamoDB
- ✅ Listagem de tabelas existentes
- ✅ Visualização de informações detalhadas
- ✅ Exclusão de tabelas
- ✅ Interface web moderna e responsiva
- ✅ Validações de negócio
- ✅ Integração com AWS via boto3

## 🏗️ Estrutura do Projeto

```
app/
├── src/
│   ├── service/           # Camada de serviço (conexões AWS)
│   │   └── dynamodb_service.py
│   ├── business/          # Camada de negócio (regras)
│   │   └── dynamodb_business.py
│   └── controller/        # Camada de controle (rotas Flask)
│       └── dynamodb_controller.py
├── templates/             # Templates HTML
│   ├── base.html
│   └── dynamodb/
│       └── index.html
├── static/               # Arquivos estáticos
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── dynamodb.js
├── app.py               # Arquivo principal
├── requirements.txt     # Dependências
├── .env.example        # Exemplo de variáveis de ambiente
└── README.md           # Este arquivo
```

## 🚀 Instalação

### 1. Clone o repositório ou navegue até a pasta do projeto

```bash
cd app
```

### 2. Crie um ambiente virtual Python

```bash
python -m venv venv
```

### 3. Ative o ambiente virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Configure as variáveis de ambiente

Copie o arquivo `.env.example` para `.env`:

```bash
copy .env.example .env
```

Edite o arquivo `.env` e configure suas credenciais AWS:

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=sua_access_key_aqui
AWS_SECRET_ACCESS_KEY=sua_secret_key_aqui
FLASK_ENV=development
FLASK_DEBUG=True
```

## 🔑 Configuração AWS

### Opção 1: Usando AWS Toolkit (Recomendado)

Se você está usando o AWS Toolkit no VS Code, as credenciais serão carregadas automaticamente. Certifique-se de:

1. Ter o AWS Toolkit instalado
2. Estar conectado à sua conta AWS
3. Ter as permissões necessárias para DynamoDB

### Opção 2: Usando arquivo .env

Configure as credenciais diretamente no arquivo `.env` conforme mostrado acima.

### Opção 3: AWS CLI

Se você já tem o AWS CLI configurado, o boto3 usará automaticamente essas credenciais.

## ▶️ Executando a Aplicação

```bash
python app.py
```

A aplicação estará disponível em: `http://localhost:5000`

## 📖 Como Usar

### Criar uma Tabela

1. Acesse a aplicação no navegador
2. Preencha o formulário "Criar Nova Tabela":
   - **Nome da Tabela**: Nome único para sua tabela (3-255 caracteres)
   - **Chave Primária**: Nome do atributo que será a chave primária
   - **Tipo da Chave**: Escolha entre String (S), Number (N) ou Binary (B)
3. Clique em "Criar Tabela"

### Listar Tabelas

As tabelas existentes são carregadas automaticamente na seção "Tabelas Existentes".

### Ver Informações de uma Tabela

Clique no botão de informações (ℹ️) ao lado do nome da tabela.

### Deletar uma Tabela

Clique no botão de deletar (🗑️) e confirme a ação.

## 🔒 Permissões AWS Necessárias

Sua conta AWS precisa das seguintes permissões no DynamoDB:

- `dynamodb:CreateTable`
- `dynamodb:ListTables`
- `dynamodb:DescribeTable`
- `dynamodb:DeleteTable`

## 🛠️ Tecnologias Utilizadas

- **Backend:**
  - Flask 3.0.0
  - boto3 1.34.0 (AWS SDK)
  - python-dotenv 1.0.0

- **Frontend:**
  - Bootstrap 5.3.0
  - Bootstrap Icons
  - JavaScript (Vanilla)

## 📝 Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/dynamodb/` | Página principal |
| POST | `/dynamodb/create` | Criar nova tabela |
| GET | `/dynamodb/list` | Listar todas as tabelas |
| GET | `/dynamodb/info/<table_name>` | Informações de uma tabela |
| DELETE | `/dynamodb/delete/<table_name>` | Deletar uma tabela |

## 🧪 Exemplo de Requisição

### Criar Tabela

```bash
curl -X POST http://localhost:5000/dynamodb/create \
  -H "Content-Type: application/json" \
  -d '{
    "table_name": "usuarios",
    "primary_key": "id",
    "primary_key_type": "S"
  }'
```

## ⚠️ Notas Importantes

1. **Billing Mode**: As tabelas são criadas com modo `PAY_PER_REQUEST` (on-demand)
2. **Região**: Certifique-se de configurar a região correta no arquivo `.env`
3. **Segurança**: Nunca commite o arquivo `.env` com credenciais reais
4. **Produção**: Para ambiente de produção, use variáveis de ambiente do sistema ou AWS Secrets Manager

## 🐛 Troubleshooting

### Erro de Credenciais AWS

```
Unable to locate credentials
```

**Solução**: Verifique se o arquivo `.env` está configurado corretamente ou se o AWS CLI está configurado.

### Erro de Permissão

```
AccessDeniedException
```

**Solução**: Verifique se sua conta AWS tem as permissões necessárias para DynamoDB.

### Tabela já existe

```
ResourceInUseException
```

**Solução**: A tabela já existe. Escolha outro nome ou delete a tabela existente.

## 📄 Licença

Este projeto é um POC (Proof of Concept) para fins educacionais.

## 👨‍💻 Autor

Desenvolvido como parte do projeto de desconto-ferramenta-operacional.
