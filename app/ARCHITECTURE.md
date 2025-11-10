# 🏗️ Arquitetura do Projeto

## Visão Geral

Este projeto segue o padrão **MVC (Model-View-Controller)** adaptado para Flask, com uma camada adicional de **Service** para gerenciar conexões externas.

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENTE (Browser)                     │
│                  HTML + JavaScript                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP Requests
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  CONTROLLER LAYER                        │
│              (Flask Blueprint Routes)                    │
│                                                          │
│  • dynamodb_controller.py                               │
│    - GET  /dynamodb/                                     │
│    - POST /dynamodb/create                               │
│    - GET  /dynamodb/list                                 │
│    - GET  /dynamodb/info/<table_name>                    │
│    - DELETE /dynamodb/delete/<table_name>                │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Chama Business Logic
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   BUSINESS LAYER                         │
│              (Regras de Negócio)                         │
│                                                          │
│  • dynamodb_business.py                                  │
│    - Validações de entrada                               │
│    - Regras de negócio                                   │
│    - Verificações de duplicidade                         │
│    - Formatação de dados                                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Chama Service
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   SERVICE LAYER                          │
│            (Conexões e Operações AWS)                    │
│                                                          │
│  • dynamodb_service.py                                   │
│    - Conexão com AWS via boto3                           │
│    - Operações CRUD no DynamoDB                          │
│    - Tratamento de erros AWS                             │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ boto3 SDK
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    AWS DynamoDB                          │
│                 (Banco de Dados NoSQL)                   │
└─────────────────────────────────────────────────────────┘
```

## 📁 Estrutura de Diretórios

```
app/
│
├── 📄 app.py                    # Aplicação Flask principal
├── 📄 run.py                    # Script de inicialização
├── 📄 config.py                 # Configurações centralizadas
├── 📄 requirements.txt          # Dependências Python
├── 📄 .env.example              # Exemplo de variáveis de ambiente
├── 📄 .gitignore                # Arquivos ignorados pelo Git
│
├── 📄 README.md                 # Documentação completa
├── 📄 QUICKSTART.md             # Guia rápido
├── 📄 ARCHITECTURE.md           # Este arquivo
│
├── 🔧 setup.bat                 # Script de instalação (Windows)
├── 🔧 start.bat                 # Script de inicialização (Windows)
│
├── 📂 src/                      # Código fonte
│   ├── 📄 __init__.py
│   │
│   ├── 📂 service/              # Camada de Serviço
│   │   ├── 📄 __init__.py
│   │   └── 📄 dynamodb_service.py
│   │
│   ├── 📂 business/             # Camada de Negócio
│   │   ├── 📄 __init__.py
│   │   └── 📄 dynamodb_business.py
│   │
│   └── 📂 controller/           # Camada de Controle
│       ├── 📄 __init__.py
│       └── 📄 dynamodb_controller.py
│
├── 📂 templates/                # Templates HTML (View)
│   ├── 📄 base.html
│   └── 📂 dynamodb/
│       └── 📄 index.html
│
└── 📂 static/                   # Arquivos estáticos
    ├── 📂 css/
    │   └── 📄 style.css
    └── 📂 js/
        └── 📄 dynamodb.js
```

## 🔄 Fluxo de Dados

### Criação de Tabela (Exemplo)

```
1. USUÁRIO preenche formulário
   ↓
2. JavaScript (dynamodb.js) captura dados
   ↓
3. Envia POST /dynamodb/create
   ↓
4. CONTROLLER (dynamodb_controller.py)
   - Recebe requisição
   - Extrai dados JSON
   ↓
5. BUSINESS (dynamodb_business.py)
   - Valida nome da tabela (3-255 chars)
   - Valida chave primária
   - Valida tipo da chave (S, N, B)
   - Verifica se tabela já existe
   ↓
6. SERVICE (dynamodb_service.py)
   - Cria cliente boto3
   - Chama create_table() da AWS
   - Trata erros do AWS
   ↓
7. AWS DynamoDB
   - Cria a tabela
   - Retorna resposta
   ↓
8. Resposta volta pela cadeia
   ↓
9. JavaScript exibe mensagem de sucesso/erro
```

## 🎯 Responsabilidades de Cada Camada

### 📱 VIEW (Templates + JavaScript)
- **Responsabilidade**: Interface com o usuário
- **Tecnologias**: HTML, Bootstrap, JavaScript
- **Arquivos**: 
  - `templates/base.html`
  - `templates/dynamodb/index.html`
  - `static/js/dynamodb.js`
  - `static/css/style.css`

### 🎮 CONTROLLER (Flask Blueprint)
- **Responsabilidade**: Gerenciar rotas HTTP
- **Tecnologias**: Flask, Blueprint
- **Arquivo**: `src/controller/dynamodb_controller.py`
- **Funções**:
  - Receber requisições HTTP
  - Extrair parâmetros
  - Chamar business layer
  - Retornar respostas JSON

### 💼 BUSINESS (Regras de Negócio)
- **Responsabilidade**: Lógica de negócio e validações
- **Tecnologias**: Python puro
- **Arquivo**: `src/business/dynamodb_business.py`
- **Funções**:
  - Validar dados de entrada
  - Aplicar regras de negócio
  - Verificar duplicidades
  - Formatar dados

### 🔌 SERVICE (Conexões Externas)
- **Responsabilidade**: Comunicação com AWS
- **Tecnologias**: boto3
- **Arquivo**: `src/service/dynamodb_service.py`
- **Funções**:
  - Gerenciar conexão boto3
  - Executar operações DynamoDB
  - Tratar erros AWS
  - Retornar dados formatados

## 🔐 Segurança

### Variáveis de Ambiente (.env)
```
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=***
AWS_SECRET_ACCESS_KEY=***
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=***
```

### Boas Práticas Implementadas
- ✅ Credenciais em variáveis de ambiente
- ✅ Validação de entrada em múltiplas camadas
- ✅ Tratamento de erros robusto
- ✅ CORS configurável
- ✅ Separação de responsabilidades

## 📊 Tecnologias Utilizadas

| Camada | Tecnologia | Versão | Propósito |
|--------|-----------|--------|-----------|
| Backend | Flask | 3.0.0 | Framework web |
| AWS SDK | boto3 | 1.34.0 | Integração AWS |
| Config | python-dotenv | 1.0.0 | Variáveis de ambiente |
| Frontend | Bootstrap | 5.3.0 | UI Framework |
| Frontend | JavaScript | ES6+ | Interatividade |
| Icons | Bootstrap Icons | 1.11.0 | Ícones |

## 🚀 Extensibilidade

### Como Adicionar Novas Funcionalidades

1. **Criar novo Service** (se necessário)
   ```python
   # src/service/novo_service.py
   class NovoService:
       def operacao(self):
           pass
   ```

2. **Criar Business Logic**
   ```python
   # src/business/novo_business.py
   class NovoBusiness:
       def __init__(self):
           self.service = NovoService()
   ```

3. **Criar Controller**
   ```python
   # src/controller/novo_controller.py
   novo_bp = Blueprint('novo', __name__)
   ```

4. **Registrar Blueprint**
   ```python
   # app.py
   from src.controller.novo_controller import novo_bp
   app.register_blueprint(novo_bp)
   ```

5. **Criar View**
   ```html
   <!-- templates/novo/index.html -->
   ```

## 📈 Melhorias Futuras

- [ ] Autenticação de usuários
- [ ] Suporte a Sort Keys (chaves de ordenação)
- [ ] Gerenciamento de índices secundários
- [ ] CRUD completo de itens nas tabelas
- [ ] Exportação/Importação de dados
- [ ] Logs de auditoria
- [ ] Testes unitários e de integração
- [ ] Docker containerization
- [ ] CI/CD pipeline

## 📞 Suporte

Para dúvidas sobre a arquitetura, consulte:
- `README.md` - Documentação geral
- `QUICKSTART.md` - Guia rápido de início
- Código fonte - Comentários inline
