# 📡 Exemplos de Uso da API

Este documento contém exemplos práticos de como usar a API REST do DynamoDB Manager.

## 🌐 Base URL

```
http://localhost:5000
```

---

## 📋 Endpoints Disponíveis

### 1. Criar Tabela

**Endpoint:** `POST /dynamodb/create`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "table_name": "usuarios",
  "primary_key": "id",
  "primary_key_type": "S"
}
```

**Tipos de Chave Válidos:**
- `S` - String
- `N` - Number
- `B` - Binary

**Exemplo com cURL:**
```bash
curl -X POST http://localhost:5000/dynamodb/create \
  -H "Content-Type: application/json" \
  -d '{
    "table_name": "usuarios",
    "primary_key": "id",
    "primary_key_type": "S"
  }'
```

**Exemplo com PowerShell:**
```powershell
$body = @{
    table_name = "usuarios"
    primary_key = "id"
    primary_key_type = "S"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/dynamodb/create" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

**Resposta de Sucesso (201):**
```json
{
  "success": true,
  "message": "Tabela usuarios criada com sucesso!",
  "data": {
    "TableDescription": {
      "TableName": "usuarios",
      "TableStatus": "CREATING",
      "CreationDateTime": "2024-01-01T10:00:00.000Z"
    }
  }
}
```

**Resposta de Erro (400):**
```json
{
  "success": false,
  "message": "Validação falhou",
  "errors": [
    "O nome da tabela deve ter entre 3 e 255 caracteres"
  ]
}
```

---

### 2. Listar Tabelas

**Endpoint:** `GET /dynamodb/list`

**Exemplo com cURL:**
```bash
curl http://localhost:5000/dynamodb/list
```

**Exemplo com PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/dynamodb/list" -Method GET
```

**Exemplo com JavaScript (Fetch):**
```javascript
fetch('http://localhost:5000/dynamodb/list')
  .then(response => response.json())
  .then(data => console.log(data));
```

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "tables": [
    "usuarios",
    "produtos",
    "pedidos"
  ]
}
```

---

### 3. Obter Informações de uma Tabela

**Endpoint:** `GET /dynamodb/info/<table_name>`

**Exemplo com cURL:**
```bash
curl http://localhost:5000/dynamodb/info/usuarios
```

**Exemplo com PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/dynamodb/info/usuarios" -Method GET
```

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "data": {
    "TableName": "usuarios",
    "TableStatus": "ACTIVE",
    "CreationDateTime": "2024-01-01T10:00:00.000Z",
    "ItemCount": 0,
    "TableSizeBytes": 0,
    "KeySchema": [
      {
        "AttributeName": "id",
        "KeyType": "HASH"
      }
    ],
    "AttributeDefinitions": [
      {
        "AttributeName": "id",
        "AttributeType": "S"
      }
    ],
    "BillingModeSummary": {
      "BillingMode": "PAY_PER_REQUEST"
    }
  }
}
```

**Resposta de Erro (404):**
```json
{
  "success": false,
  "message": "Erro ao descrever tabela: Requested resource not found"
}
```

---

### 4. Deletar Tabela

**Endpoint:** `DELETE /dynamodb/delete/<table_name>`

**Exemplo com cURL:**
```bash
curl -X DELETE http://localhost:5000/dynamodb/delete/usuarios
```

**Exemplo com PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/dynamodb/delete/usuarios" -Method DELETE
```

**Exemplo com JavaScript (Fetch):**
```javascript
fetch('http://localhost:5000/dynamodb/delete/usuarios', {
  method: 'DELETE'
})
  .then(response => response.json())
  .then(data => console.log(data));
```

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "message": "Tabela usuarios deletada com sucesso!",
  "data": {
    "TableDescription": {
      "TableName": "usuarios",
      "TableStatus": "DELETING"
    }
  }
}
```

---

## 🧪 Cenários de Teste

### Cenário 1: Criar e Listar Tabelas

```bash
# 1. Criar tabela de usuários
curl -X POST http://localhost:5000/dynamodb/create \
  -H "Content-Type: application/json" \
  -d '{"table_name": "usuarios", "primary_key": "id", "primary_key_type": "S"}'

# 2. Criar tabela de produtos
curl -X POST http://localhost:5000/dynamodb/create \
  -H "Content-Type: application/json" \
  -d '{"table_name": "produtos", "primary_key": "sku", "primary_key_type": "S"}'

# 3. Listar todas as tabelas
curl http://localhost:5000/dynamodb/list
```

### Cenário 2: Validação de Erros

```bash
# Tentar criar tabela com nome muito curto
curl -X POST http://localhost:5000/dynamodb/create \
  -H "Content-Type: application/json" \
  -d '{"table_name": "ab", "primary_key": "id", "primary_key_type": "S"}'

# Resposta esperada: Erro de validação
```

### Cenário 3: Ciclo Completo

```bash
# 1. Criar tabela
curl -X POST http://localhost:5000/dynamodb/create \
  -H "Content-Type: application/json" \
  -d '{"table_name": "teste", "primary_key": "id", "primary_key_type": "S"}'

# 2. Ver informações
curl http://localhost:5000/dynamodb/info/teste

# 3. Deletar tabela
curl -X DELETE http://localhost:5000/dynamodb/delete/teste

# 4. Verificar que foi deletada
curl http://localhost:5000/dynamodb/list
```

---

## 🐍 Exemplo com Python (requests)

```python
import requests
import json

BASE_URL = "http://localhost:5000"

# Criar tabela
def criar_tabela(nome, chave, tipo='S'):
    url = f"{BASE_URL}/dynamodb/create"
    payload = {
        "table_name": nome,
        "primary_key": chave,
        "primary_key_type": tipo
    }
    response = requests.post(url, json=payload)
    return response.json()

# Listar tabelas
def listar_tabelas():
    url = f"{BASE_URL}/dynamodb/list"
    response = requests.get(url)
    return response.json()

# Obter informações
def info_tabela(nome):
    url = f"{BASE_URL}/dynamodb/info/{nome}"
    response = requests.get(url)
    return response.json()

# Deletar tabela
def deletar_tabela(nome):
    url = f"{BASE_URL}/dynamodb/delete/{nome}"
    response = requests.delete(url)
    return response.json()

# Uso
if __name__ == "__main__":
    # Criar
    print(criar_tabela("usuarios", "id", "S"))
    
    # Listar
    print(listar_tabelas())
    
    # Info
    print(info_tabela("usuarios"))
    
    # Deletar
    print(deletar_tabela("usuarios"))
```

---

## 🌐 Exemplo com JavaScript (Node.js)

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:5000';

// Criar tabela
async function criarTabela(nome, chave, tipo = 'S') {
  try {
    const response = await axios.post(`${BASE_URL}/dynamodb/create`, {
      table_name: nome,
      primary_key: chave,
      primary_key_type: tipo
    });
    return response.data;
  } catch (error) {
    return error.response.data;
  }
}

// Listar tabelas
async function listarTabelas() {
  try {
    const response = await axios.get(`${BASE_URL}/dynamodb/list`);
    return response.data;
  } catch (error) {
    return error.response.data;
  }
}

// Obter informações
async function infoTabela(nome) {
  try {
    const response = await axios.get(`${BASE_URL}/dynamodb/info/${nome}`);
    return response.data;
  } catch (error) {
    return error.response.data;
  }
}

// Deletar tabela
async function deletarTabela(nome) {
  try {
    const response = await axios.delete(`${BASE_URL}/dynamodb/delete/${nome}`);
    return response.data;
  } catch (error) {
    return error.response.data;
  }
}

// Uso
(async () => {
  console.log(await criarTabela('usuarios', 'id', 'S'));
  console.log(await listarTabelas());
  console.log(await infoTabela('usuarios'));
  console.log(await deletarTabela('usuarios'));
})();
```

---

## ⚠️ Códigos de Status HTTP

| Código | Significado | Quando ocorre |
|--------|-------------|---------------|
| 200 | OK | Operação bem-sucedida (GET, DELETE) |
| 201 | Created | Tabela criada com sucesso |
| 400 | Bad Request | Validação falhou ou erro na requisição |
| 404 | Not Found | Tabela não encontrada |
| 500 | Internal Server Error | Erro no servidor |

---

## 🔍 Dicas de Debugging

### Ver logs detalhados
Execute a aplicação com debug ativado:
```bash
python app.py
```

### Testar conectividade
```bash
curl http://localhost:5000/dynamodb/list
```

### Verificar formato JSON
Use ferramentas como:
- Postman
- Insomnia
- Thunder Client (VS Code)

---

## 📚 Recursos Adicionais

- [Documentação boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [DynamoDB Developer Guide](https://docs.aws.amazon.com/dynamodb/)
- [Flask Documentation](https://flask.palletsprojects.com/)
