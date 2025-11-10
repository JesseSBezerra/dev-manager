# 🔧 Guia de Solução de Problemas

## ❌ Erro: "The security token included in the request is invalid"

### Causa
Este erro ocorre quando o boto3 não consegue encontrar credenciais AWS válidas.

### ✅ Solução para AWS Toolkit (Recomendado)

1. **Verifique se o AWS Toolkit está instalado no VS Code**
   - Extensão: AWS Toolkit

2. **Conecte-se à sua conta AWS**
   - Clique no ícone AWS na barra lateral
   - Escolha "Connect to AWS"
   - Selecione seu perfil/credenciais

3. **Crie um arquivo `.env` VAZIO ou com apenas a região**
   ```bash
   # No terminal, na pasta do projeto:
   echo AWS_REGION=us-east-1 > .env
   ```
   
   **OU** copie o `.env.example`:
   ```bash
   copy .env.example .env
   ```
   
   **IMPORTANTE**: Deixe `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` vazios!

4. **Reinicie a aplicação Flask**
   ```bash
   python app.py
   ```

### ✅ Solução para AWS CLI

Se você usa AWS CLI configurado:

1. **Verifique se está configurado**
   ```bash
   aws configure list
   ```

2. **Crie arquivo `.env` apenas com a região**
   ```bash
   echo AWS_REGION=us-east-1 > .env
   ```

3. **Reinicie a aplicação**

### ✅ Solução com Credenciais Explícitas

Se você quer usar credenciais diretas no `.env`:

1. **Copie o arquivo de exemplo**
   ```bash
   copy .env.example .env
   ```

2. **Edite o `.env` e preencha**
   ```env
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
   AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   ```

3. **Reinicie a aplicação**

---

## 🔍 Como o boto3 busca credenciais

O boto3 procura credenciais nesta ordem:

1. ✅ **Parâmetros explícitos** no código (quando `.env` tem credenciais)
2. ✅ **Variáveis de ambiente** do sistema
3. ✅ **Arquivo `~/.aws/credentials`** (AWS CLI)
4. ✅ **AWS Toolkit** / SSO
5. ✅ **IAM Role** (se estiver em EC2/ECS)

---

## ❌ Erro: "Unable to locate credentials"

### Causa
Nenhuma credencial foi encontrada em nenhum dos métodos acima.

### Solução
Escolha **UMA** das opções:
- Configure o AWS Toolkit
- Configure o AWS CLI (`aws configure`)
- Preencha o arquivo `.env`

---

## ❌ Erro: "Access Denied" ou "UnauthorizedException"

### Causa
Suas credenciais não têm permissão para acessar o DynamoDB.

### Solução
Verifique se sua conta/usuário AWS tem as permissões:
- `dynamodb:CreateTable`
- `dynamodb:ListTables`
- `dynamodb:DescribeTable`
- `dynamodb:DeleteTable`

---

## ❌ Erro: "Region not specified"

### Causa
A região AWS não foi configurada.

### Solução
Crie/edite o arquivo `.env`:
```env
AWS_REGION=us-east-1
```

Ou defina como variável de ambiente do sistema:
```bash
# Windows PowerShell
$env:AWS_REGION="us-east-1"

# Windows CMD
set AWS_REGION=us-east-1
```

---

## ❌ Erro: "ResourceInUseException"

### Causa
A tabela que você está tentando criar já existe.

### Solução
- Escolha outro nome para a tabela
- Ou delete a tabela existente primeiro

---

## ❌ Erro: "ValidationException"

### Causa
Os dados enviados não são válidos (nome muito curto, caracteres inválidos, etc.)

### Solução
Verifique as regras:
- Nome da tabela: 3-255 caracteres
- Caracteres permitidos: letras, números, `_`, `-`, `.`
- Chave primária: 1-255 caracteres
- Tipo da chave: `S`, `N`, ou `B`

---

## 🧪 Testando a Conexão AWS

Execute este script Python para testar:

```python
import boto3

try:
    # Tenta listar tabelas
    client = boto3.client('dynamodb', region_name='us-east-1')
    response = client.list_tables()
    print("✅ Conexão OK!")
    print(f"Tabelas encontradas: {response['TableNames']}")
except Exception as e:
    print(f"❌ Erro: {e}")
```

Salve como `test_aws.py` e execute:
```bash
python test_aws.py
```

---

## 📞 Ainda com problemas?

1. **Verifique os logs da aplicação** - Erros detalhados aparecem no console
2. **Teste a conexão AWS** com o script acima
3. **Verifique o AWS Toolkit** - Deve mostrar "Connected" no VS Code
4. **Reinicie o VS Code** - Às vezes o Toolkit precisa ser reiniciado

---

## ✅ Checklist Rápido

- [ ] AWS Toolkit instalado e conectado
- [ ] Arquivo `.env` existe (pode estar vazio ou só com região)
- [ ] Região AWS configurada (`AWS_REGION=us-east-1`)
- [ ] Credenciais do `.env` estão vazias (para usar Toolkit)
- [ ] Aplicação Flask reiniciada após mudanças
- [ ] Permissões DynamoDB configuradas na conta AWS

---

## 💡 Dica Pro

Para desenvolvimento, use **AWS Toolkit** - é mais seguro e prático:
- ✅ Não precisa expor credenciais em arquivos
- ✅ Suporta múltiplos perfis
- ✅ Integração nativa com VS Code
- ✅ Renovação automática de tokens
