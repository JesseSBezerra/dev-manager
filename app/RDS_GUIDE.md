# 🗄️ Guia de Uso - RDS (Relational Database Service)

## 📋 Visão Geral

O módulo RDS permite criar e gerenciar bancos de dados relacionais na AWS de forma simples através de uma interface web intuitiva.

## 🎯 Funcionalidades

### ✅ Criar Instâncias RDS
- Crie bancos de dados MySQL, PostgreSQL, MariaDB, Oracle e SQL Server
- Configure classe da instância, storage e opções de alta disponibilidade
- Defina usuário e senha master
- Escolha entre acesso público ou privado
- Habilite Multi-AZ para alta disponibilidade

### ✅ Listar Instâncias
- Visualize todas as instâncias RDS da sua região
- Veja status em tempo real
- Informações exibidas:
  - Identificador
  - Status (available, stopped, creating, etc.)
  - Engine e versão
  - Classe da instância
  - Storage alocado
  - Multi-AZ
  - Endpoint de conexão

### ✅ Gerenciar Instâncias

#### ⏸️ Parar Instância
- Para instâncias para economizar custos
- Você paga apenas por storage quando parado
- Útil para ambientes de desenvolvimento/teste

#### ▶️ Iniciar Instância
- Inicia instâncias paradas
- Leva alguns minutos para ficar disponível

#### 🗑️ Deletar Instância
- Remove instâncias permanentemente
- Opção de criar snapshot final (recomendado)
- Ação irreversível

### ✅ Ver Detalhes
- Endpoint de conexão
- Configurações completas
- Informações de backup
- Status detalhado

## 🚀 Como Usar

### 1. Acessar o Módulo RDS

```
http://localhost:5000/rds
```

Ou clique em **"RDS"** no menu de navegação.

### 2. Criar uma Nova Instância

1. Clique em **"Criar Nova Instância RDS"**
2. Preencha o formulário:

**Campos obrigatórios:**
- **Identificador**: Nome único (ex: `my-database-prod`)
  - Apenas letras minúsculas, números e hífens
  - Deve começar com letra
  - 1-63 caracteres

- **Engine**: Escolha o banco de dados
  - MySQL
  - PostgreSQL
  - MariaDB
  - Oracle SE2
  - SQL Server Express

- **Classe da Instância**: Tamanho da instância
  - `db.t3.micro`: 1 vCPU, 1 GB RAM (Free Tier elegível)
  - `db.t3.small`: 2 vCPU, 2 GB RAM
  - `db.t3.medium`: 2 vCPU, 4 GB RAM
  - `db.m5.large`: 2 vCPU, 8 GB RAM (produção)

- **Armazenamento**: Tamanho em GB (mínimo 20 GB)

- **Usuário Master**: Nome do usuário administrador
  - 1-16 caracteres
  - Evite palavras reservadas (admin, root, postgres)

- **Senha Master**: Senha do administrador
  - 8-41 caracteres
  - Use senha forte!

**Campos opcionais:**
- **Nome do Banco**: Nome do banco inicial
- **Acesso Público**: Se a instância será acessível pela internet
- **Multi-AZ**: Alta disponibilidade (replicação automática)

3. Clique em **"Criar Instância"**
4. Aguarde 5-15 minutos para a criação

### 3. Conectar ao Banco de Dados

Após a instância ficar **available**:

1. Clique no botão de **detalhes** (ℹ️)
2. Copie o **Endpoint**
3. Use em sua aplicação:

**Exemplo MySQL:**
```bash
mysql -h my-database.abc123.sa-east-1.rds.amazonaws.com -P 3306 -u admin -p
```

**Exemplo PostgreSQL:**
```bash
psql -h my-database.abc123.sa-east-1.rds.amazonaws.com -p 5432 -U admin -d mydatabase
```

**String de conexão (Python):**
```python
import pymysql

connection = pymysql.connect(
    host='my-database.abc123.sa-east-1.rds.amazonaws.com',
    user='admin',
    password='sua-senha',
    database='mydatabase',
    port=3306
)
```

### 4. Gerenciar Instâncias

**Parar uma instância:**
- Clique no botão ⏸️ (amarelo)
- Confirme a ação
- A instância será parada em alguns minutos

**Iniciar uma instância:**
- Clique no botão ▶️ (verde)
- Confirme a ação
- A instância levará alguns minutos para iniciar

**Deletar uma instância:**
- Clique no botão 🗑️ (vermelho)
- Escolha se quer criar snapshot final (recomendado)
- Confirme a exclusão
- **ATENÇÃO**: Esta ação é irreversível!

## 📊 Endpoints da API

### Listar Instâncias
```
GET /rds/instances
```

**Resposta:**
```json
{
  "success": true,
  "instances": [
    {
      "identifier": "my-database",
      "status": "available",
      "engine": "mysql",
      "engine_version": "8.0.35",
      "instance_class": "db.t3.micro",
      "storage": 20,
      "endpoint": "my-database.abc123.sa-east-1.rds.amazonaws.com",
      "port": 3306
    }
  ],
  "count": 1
}
```

### Criar Instância
```
POST /rds/instances
Content-Type: application/json

{
  "db_instance_identifier": "my-database",
  "db_instance_class": "db.t3.micro",
  "engine": "mysql",
  "master_username": "admin",
  "master_password": "MySecurePassword123",
  "allocated_storage": 20,
  "db_name": "mydatabase",
  "publicly_accessible": false,
  "multi_az": false
}
```

### Parar Instância
```
POST /rds/instances/{identifier}/stop
```

### Iniciar Instância
```
POST /rds/instances/{identifier}/start
```

### Deletar Instância
```
DELETE /rds/instances/{identifier}?skip_final_snapshot=false
```

## 💰 Custos

### Free Tier (12 meses)
- 750 horas/mês de `db.t3.micro` (MySQL, PostgreSQL ou MariaDB)
- 20 GB de storage
- 20 GB de backup

### Instâncias Paradas
- **Não cobra** por computação
- **Cobra** por storage (GB/mês)
- Economia de ~70% dos custos

### Exemplo de Custos (sa-east-1)
- `db.t3.micro`: ~$0.018/hora = ~$13/mês
- `db.t3.small`: ~$0.036/hora = ~$26/mês
- `db.t3.medium`: ~$0.072/hora = ~$52/mês
- Storage (gp2): ~$0.138/GB/mês

## 🔒 Permissões AWS Necessárias

### Permissões de Leitura
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "rds:DescribeDBInstances"
      ],
      "Resource": "*"
    }
  ]
}
```

### Permissões de Escrita
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "rds:CreateDBInstance",
        "rds:DeleteDBInstance",
        "rds:StopDBInstance",
        "rds:StartDBInstance",
        "rds:ModifyDBInstance"
      ],
      "Resource": "arn:aws:rds:*:*:db:*"
    }
  ]
}
```

## 🔐 Segurança

### Boas Práticas

1. **Senhas Fortes**
   - Use senhas com 16+ caracteres
   - Combine letras, números e símbolos
   - Não use senhas óbvias

2. **Acesso Privado**
   - Mantenha `publicly_accessible = false`
   - Use VPC e Security Groups
   - Acesse via VPN ou bastion host

3. **Criptografia**
   - Todas as instâncias são criadas com criptografia habilitada
   - Backups também são criptografados

4. **Backups**
   - Retenção padrão: 7 dias
   - Crie snapshots manuais antes de mudanças importantes
   - Teste restauração de backups regularmente

5. **Multi-AZ**
   - Use em produção para alta disponibilidade
   - Failover automático em caso de falha
   - Custo: ~2x o preço da instância

## ⚠️ Limitações

- **Tempo de criação**: 5-15 minutos
- **Instâncias paradas**: Reiniciam automaticamente após 7 dias
- **Modificações**: Algumas requerem reinicialização
- **Região única**: Mostra apenas recursos da região configurada

## 💡 Dicas

### Desenvolvimento
- Use `db.t3.micro` (Free Tier)
- Pare instâncias fora do horário de trabalho
- Não use Multi-AZ

### Produção
- Use classes maiores (`db.m5.large+`)
- Habilite Multi-AZ
- Configure backup retention adequado
- Use acesso privado (VPC)

### Economia de Custos
1. **Pare instâncias não usadas**
   - Dev/Test fora do horário
   - Economia de ~70%

2. **Use Reserved Instances**
   - Desconto de até 69% para 1-3 anos
   - Ideal para produção

3. **Monitore o uso**
   - Delete instâncias não utilizadas
   - Ajuste classe conforme necessidade

## 🐛 Troubleshooting

### Instância não inicia
- Verifique se há problemas de quota na conta AWS
- Confirme que a região está correta
- Verifique logs no CloudWatch

### Não consigo conectar
- Verifique Security Groups
- Confirme que `publicly_accessible` está correto
- Teste conectividade de rede

### Erro ao criar
- Verifique se o identificador já existe
- Confirme que a senha atende aos requisitos
- Verifique permissões AWS

### Instância muito lenta
- Considere aumentar a classe
- Verifique métricas no CloudWatch
- Avalie uso de IOPS provisionado

## 📚 Recursos Adicionais

- [Documentação AWS RDS](https://docs.aws.amazon.com/rds/)
- [Guia de Melhores Práticas](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)
- [Calculadora de Preços AWS](https://calculator.aws/)
- [boto3 RDS Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds.html)

## 🎯 Próximas Funcionalidades (Roadmap)

- [ ] Modificar instâncias (alterar classe/storage)
- [ ] Criar/restaurar snapshots
- [ ] Configurar parameter groups
- [ ] Visualizar métricas do CloudWatch
- [ ] Configurar alertas
- [ ] Suporte a Read Replicas
- [ ] Gerenciar Security Groups
- [ ] Logs de auditoria
