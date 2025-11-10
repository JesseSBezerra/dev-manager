# 🚀 Guia Rápido de Início

## Passos para executar a aplicação:

### 1️⃣ Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2️⃣ Configurar AWS

**Opção A - Usando arquivo .env (Recomendado para desenvolvimento):**

```bash
# Copie o arquivo de exemplo
copy .env.example .env

# Edite o .env e adicione suas credenciais AWS
```

**Opção B - Usando AWS Toolkit:**
- Instale o AWS Toolkit no VS Code
- Conecte-se à sua conta AWS
- As credenciais serão carregadas automaticamente

**Opção C - Usando AWS CLI:**
```bash
aws configure
```

### 3️⃣ Executar a Aplicação

```bash
python app.py
```

ou

```bash
python run.py
```

### 4️⃣ Acessar no Navegador

Abra: `http://localhost:5000`

---

## 📋 Exemplo de uso:

1. **Criar uma tabela:**
   - Nome: `usuarios`
   - Chave Primária: `id`
   - Tipo: `String (S)`

2. **Visualizar tabelas criadas** na seção "Tabelas Existentes"

3. **Ver informações** clicando no ícone ℹ️

4. **Deletar tabela** clicando no ícone 🗑️

---

## ⚠️ Problemas Comuns:

### Erro de credenciais AWS
```
Unable to locate credentials
```
**Solução:** Configure o arquivo `.env` com suas credenciais AWS

### Porta já em uso
```
Address already in use
```
**Solução:** Altere a porta no arquivo `.env`:
```
FLASK_PORT=5001
```

### Módulo não encontrado
```
ModuleNotFoundError: No module named 'flask'
```
**Solução:** Instale as dependências:
```bash
pip install -r requirements.txt
```

---

## 📞 Precisa de Ajuda?

Consulte o arquivo `README.md` para documentação completa.
