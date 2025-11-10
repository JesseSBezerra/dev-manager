# 🔍 Guia de Uso - SQL Query Tool

## 📋 Visão Geral

O **SQL Query Tool** permite executar queries SQL diretamente no RDS através do Bastion Host, usando túnel SSM. Você pode consultar dados, inserir registros, atualizar e deletar - tudo pela interface web!

## 🎯 Funcionalidades

### ✅ Executar Queries SQL
- SELECT, INSERT, UPDATE, DELETE
- SHOW TABLES, DESCRIBE
- Qualquer comando SQL válido
- Resultados em tabela formatada
- Tempo de execução exibido

### ✅ Gerenciar Conexões
- Testar conexão antes de executar
- Suporte a MySQL, PostgreSQL, MariaDB
- Conexão via localhost (túnel SSM)
- Credenciais seguras (não armazenadas)

### ✅ Túnel SSM Automático
- Criar túnel para RDS via Bastion
- Port forwarding automático
- Conexão segura sem VPN

### ✅ Explorar Banco de Dados
- Listar todas as tabelas
- Gerar SELECT automático
- Templates de queries

## 🚀 Como Usar

### Pré-requisitos

1. **RDS criado** com banco de dados
2. **Bastion Host** rodando
3. **AWS CLI** instalado
4. **Session Manager Plugin** instalado
5. **Drivers de banco** instalados:
   ```bash
   pip install PyMySQL psycopg2-binary SQLAlchemy
   ```

### Passo 1: Criar Túnel SSM

#### Opção A: Via Interface Web

1. Acesse **SQL Query Tool** no menu
2. Clique em **"Criar Túnel SSM"**
3. Preencha:
   - **ID do Bastion**: `i-xxxxxxxxxxxxx`
   - **Endpoint do RDS**: `mydb.abc123.sa-east-1.rds.amazonaws.com`
   - **Porta do RDS**: `3306` (MySQL) ou `5432` (PostgreSQL)
   - **Porta Local**: deixe vazio (usará a mesma)
4. Clique em **"Criar Túnel"**
5. Aguarde 3-5 segundos

#### Opção B: Via Terminal (Manual)

```bash
# MySQL/MariaDB
aws ssm start-session \
  --target i-xxxxxxxxxxxxx \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters host="mydb.abc123.sa-east-1.rds.amazonaws.com",portNumber="3306",localPortNumber="3306"

# PostgreSQL
aws ssm start-session \
  --target i-xxxxxxxxxxxxx \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters host="mydb.abc123.sa-east-1.rds.amazonaws.com",portNumber="5432",localPortNumber="5432"
```

### Passo 2: Configurar Conexão

Preencha os campos de conexão:

- **Engine**: MySQL, PostgreSQL ou MariaDB
- **Host**: `localhost` (via túnel)
- **Porta**: `3306` (MySQL) ou `5432` (PostgreSQL)
- **Banco de Dados**: Nome do seu banco
- **Usuário**: Usuário master do RDS
- **Senha**: Senha master do RDS

### Passo 3: Testar Conexão

1. Clique em **"Testar Conexão"**
2. Aguarde confirmação: ✅ "Conexão estabelecida com sucesso!"
3. Se falhar, verifique:
   - Túnel SSM está ativo?
   - Credenciais corretas?
   - Security Groups permitem acesso?

### Passo 4: Executar Queries

#### SELECT (Consultar Dados)

```sql
SELECT * FROM usuarios WHERE ativo = 1;
```

**Resultado:**
- Tabela formatada com colunas e linhas
- Número de linhas retornadas
- Tempo de execução

#### INSERT (Inserir Dados)

```sql
INSERT INTO usuarios (nome, email, ativo) 
VALUES ('João Silva', 'joao@email.com', 1);
```

**Resultado:**
- "1 linha(s) afetada(s)"
- Tempo de execução

#### UPDATE (Atualizar Dados)

```sql
UPDATE usuarios 
SET ativo = 0 
WHERE id = 5;
```

#### DELETE (Deletar Dados)

```sql
DELETE FROM usuarios 
WHERE id = 10;
```

### Passo 5: Explorar Banco de Dados

1. Clique em **"Listar Tabelas"**
2. Veja todas as tabelas do banco
3. Clique em **"SELECT *"** em qualquer tabela
4. Query é inserida automaticamente no editor

## 📊 Exemplos de Queries

### Consultas Básicas

```sql
-- Listar todas as tabelas
SHOW TABLES;

-- Ver estrutura de uma tabela
DESCRIBE usuarios;

-- Selecionar tudo
SELECT * FROM produtos LIMIT 10;

-- Filtrar resultados
SELECT nome, preco FROM produtos WHERE preco > 100;

-- Ordenar resultados
SELECT * FROM pedidos ORDER BY data_criacao DESC LIMIT 20;

-- Contar registros
SELECT COUNT(*) as total FROM usuarios;
```

### Joins

```sql
-- Inner Join
SELECT u.nome, p.titulo 
FROM usuarios u 
INNER JOIN pedidos p ON u.id = p.usuario_id;

-- Left Join
SELECT u.nome, COUNT(p.id) as total_pedidos
FROM usuarios u
LEFT JOIN pedidos p ON u.id = p.usuario_id
GROUP BY u.id;
```

### Agregações

```sql
-- Soma
SELECT SUM(valor) as total_vendas FROM pedidos;

-- Média
SELECT AVG(preco) as preco_medio FROM produtos;

-- Agrupamento
SELECT categoria, COUNT(*) as quantidade
FROM produtos
GROUP BY categoria;
```

### Subconsultas

```sql
-- Subconsulta no WHERE
SELECT * FROM produtos 
WHERE preco > (SELECT AVG(preco) FROM produtos);

-- Subconsulta no FROM
SELECT categoria, avg_preco
FROM (
  SELECT categoria, AVG(preco) as avg_preco
  FROM produtos
  GROUP BY categoria
) as subquery
WHERE avg_preco > 50;
```

## 🔒 Segurança

### Boas Práticas

1. **Não armazene senhas**
   - Senhas não são salvas pela aplicação
   - Digite a cada sessão

2. **Use usuários com privilégios limitados**
   ```sql
   -- Criar usuário read-only
   CREATE USER 'readonly'@'%' IDENTIFIED BY 'senha';
   GRANT SELECT ON meudb.* TO 'readonly'@'%';
   ```

3. **Cuidado com comandos destrutivos**
   - `DROP DATABASE` é bloqueado por padrão
   - Sempre use `WHERE` em UPDATE/DELETE
   - Teste com `SELECT` antes de modificar

4. **Limite de tamanho**
   - Queries limitadas a 50KB
   - Use `LIMIT` em SELECTs grandes

### Comandos Bloqueados

Por segurança, alguns comandos são bloqueados:
- `DROP DATABASE`
- `DROP SCHEMA`

Para executá-los, use um cliente SQL direto.

## 💡 Dicas e Truques

### Atalhos de Teclado

- **Ctrl + Enter**: Executar query
- **Templates**: Clique nos botões SELECT, INSERT, UPDATE, DELETE

### Templates Rápidos

Clique nos botões para inserir templates:

**SELECT:**
```sql
SELECT * FROM tabela WHERE id = 1;
```

**INSERT:**
```sql
INSERT INTO tabela (coluna1, coluna2) VALUES (valor1, valor2);
```

**UPDATE:**
```sql
UPDATE tabela SET coluna1 = valor1 WHERE id = 1;
```

**DELETE:**
```sql
DELETE FROM tabela WHERE id = 1;
```

### Otimização de Queries

```sql
-- Use LIMIT para grandes resultados
SELECT * FROM logs LIMIT 100;

-- Use índices
SELECT * FROM usuarios WHERE email = 'teste@email.com'; -- email deve ter índice

-- Evite SELECT *
SELECT id, nome, email FROM usuarios; -- Melhor

-- Use EXPLAIN para analisar
EXPLAIN SELECT * FROM pedidos WHERE usuario_id = 5;
```

## 🐛 Troubleshooting

### Erro: "Falha na conexão"

**Causas:**
- Túnel SSM não está ativo
- Credenciais incorretas
- Security Group bloqueando

**Soluções:**
1. Verifique se o túnel está rodando
2. Teste credenciais via mysql/psql CLI
3. Verifique Security Groups

### Erro: "Connection refused"

**Causa:** Túnel SSM não foi criado

**Solução:**
```bash
# Criar túnel manualmente
aws ssm start-session --target i-xxxxx \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters host="rds-endpoint",portNumber="3306",localPortNumber="3306"
```

### Query muito lenta

**Soluções:**
1. Use `LIMIT` para reduzir resultados
2. Adicione índices nas colunas filtradas
3. Otimize a query com `EXPLAIN`

### Túnel fecha sozinho

**Causa:** Timeout de inatividade

**Solução:**
- Recrie o túnel
- Execute queries periodicamente
- Use `--idle-session-timeout` no comando SSM

## 📚 Recursos Adicionais

### MySQL
- [Documentação MySQL](https://dev.mysql.com/doc/)
- [Tutorial SQL](https://www.w3schools.com/sql/)

### PostgreSQL
- [Documentação PostgreSQL](https://www.postgresql.org/docs/)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)

### SSM Session Manager
- [Port Forwarding](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-sessions-start.html#sessions-remote-port-forwarding)

## 🎯 Casos de Uso

### 1. Análise de Dados

```sql
-- Dashboard de vendas
SELECT 
  DATE(data_pedido) as data,
  COUNT(*) as total_pedidos,
  SUM(valor) as receita_total
FROM pedidos
WHERE data_pedido >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(data_pedido)
ORDER BY data DESC;
```

### 2. Manutenção de Dados

```sql
-- Limpar registros antigos
DELETE FROM logs 
WHERE data_criacao < DATE_SUB(NOW(), INTERVAL 90 DAY);

-- Atualizar dados em lote
UPDATE produtos 
SET desconto = 10 
WHERE categoria = 'eletronicos' AND estoque > 100;
```

### 3. Debugging

```sql
-- Verificar dados inconsistentes
SELECT * FROM pedidos 
WHERE status = 'pago' AND valor_pago = 0;

-- Encontrar duplicatas
SELECT email, COUNT(*) as duplicatas
FROM usuarios
GROUP BY email
HAVING COUNT(*) > 1;
```

### 4. Relatórios

```sql
-- Top 10 clientes
SELECT u.nome, COUNT(p.id) as total_pedidos, SUM(p.valor) as total_gasto
FROM usuarios u
INNER JOIN pedidos p ON u.id = p.usuario_id
GROUP BY u.id
ORDER BY total_gasto DESC
LIMIT 10;
```

## ⚠️ Avisos Importantes

1. **Backup antes de modificar**
   - Sempre faça backup antes de UPDATE/DELETE em massa
   - Teste com SELECT primeiro

2. **Transações**
   - Use BEGIN/COMMIT para operações críticas
   - ROLLBACK em caso de erro

3. **Performance**
   - Evite queries pesadas em horário de pico
   - Use LIMIT em desenvolvimento

4. **Segurança**
   - Nunca exponha credenciais
   - Use túnel SSM sempre
   - Não compartilhe senhas

## ✅ Checklist de Uso

Antes de executar queries:

- [ ] Túnel SSM criado e ativo
- [ ] Conexão testada com sucesso
- [ ] Credenciais corretas
- [ ] Query revisada (especialmente UPDATE/DELETE)
- [ ] Backup recente (para operações destrutivas)
- [ ] LIMIT adicionado (para SELECTs grandes)
- [ ] WHERE clause presente (em UPDATE/DELETE)

---

**Pronto para executar queries SQL no RDS!** 🚀
