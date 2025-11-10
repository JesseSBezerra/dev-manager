# 🖥️ Guia de Uso - EC2 e Bastion Host com SSM

## 📋 Visão Geral

O módulo EC2 permite gerenciar instâncias EC2 e criar Bastion Hosts configurados com SSM (Systems Manager) para acesso seguro aos seus bancos de dados RDS sem expor portas SSH publicamente.

## 🎯 Funcionalidades

### ✅ Criar Bastion Host com SSM
- Instância EC2 pré-configurada para acesso seguro
- Amazon Linux 2 com SSM Agent instalado
- IAM Role automaticamente configurada
- Ferramentas pré-instaladas: mysql, postgresql, telnet, nc
- Conexão via SSM Session Manager (sem SSH público)
- Ideal para túnel seguro até RDS

### ✅ Gerenciar Instâncias EC2
- Listar todas as instâncias
- Criar instâncias genéricas
- Iniciar/Parar instâncias
- Terminar (deletar) instâncias
- Ver detalhes completos

### ✅ Conectar via SSM
- Comandos prontos para conexão
- Port Forwarding para RDS
- Sem necessidade de SSH keys
- Sem portas públicas expostas

## 🚀 Como Usar

### 1. Acessar o Módulo EC2

```
http://localhost:5000/ec2
```

Ou clique em **"EC2"** no menu de navegação.

### 2. Criar um Bastion Host

#### Passo a Passo:

1. Clique em **"Criar Bastion Host (SSM)"**
2. Preencha o formulário:
   - **Nome**: Ex: `bastion-prod`
   - **Tipo**: `t3.micro` (Free Tier elegível)
   - **Key Pair**: Opcional (deixe vazio se usar apenas SSM)
   - **Subnet ID**: Opcional (use a mesma subnet do RDS)

3. Clique em **"Criar Bastion Host"**
4. Aguarde 2-3 minutos para a instância iniciar

#### O que é criado automaticamente:

- ✅ Instância EC2 com Amazon Linux 2
- ✅ SSM Agent pré-instalado e configurado
- ✅ IAM Role `EC2-SSM-Role` com permissões SSM
- ✅ IAM Instance Profile anexado
- ✅ Ferramentas de banco de dados instaladas
- ✅ Tags: `Type=Bastion`, `ManagedBy=AWSManager`

### 3. Conectar ao Bastion via SSM

#### Requisitos:

1. **AWS CLI** instalado
2. **Session Manager Plugin** instalado

**Instalar Session Manager Plugin:**

**Windows:**
```powershell
# Download e instale:
https://s3.amazonaws.com/session-manager-downloads/plugin/latest/windows/SessionManagerPluginSetup.exe
```

**Linux/Mac:**
```bash
# Ubuntu/Debian
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "session-manager-plugin.deb"
sudo dpkg -i session-manager-plugin.deb

# Mac
brew install --cask session-manager-plugin
```

#### Conectar:

1. Na lista de instâncias, clique no botão **Terminal** (verde) do Bastion
2. Copie o comando exibido
3. Execute no seu terminal:

```bash
aws ssm start-session --target i-xxxxxxxxxxxxx --region sa-east-1
```

Você estará conectado ao Bastion Host! 🎉

### 4. Criar Túnel para RDS

Para conectar ao RDS através do Bastion:

#### Comando de Port Forwarding:

```bash
aws ssm start-session \
  --target i-xxxxxxxxxxxxx \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters host="seu-rds.abc123.sa-east-1.rds.amazonaws.com",portNumber="3306",localPortNumber="3306"
```

**Substitua:**
- `i-xxxxxxxxxxxxx` pelo ID do seu Bastion
- `seu-rds.abc123...` pelo endpoint do seu RDS
- `3306` pela porta do seu banco (3306=MySQL, 5432=PostgreSQL)

#### Conectar ao RDS:

Com o túnel ativo, conecte-se localmente:

**MySQL:**
```bash
mysql -h 127.0.0.1 -P 3306 -u admin -p
```

**PostgreSQL:**
```bash
psql -h 127.0.0.1 -p 5432 -U admin -d mydatabase
```

**Python:**
```python
import pymysql

connection = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='admin',
    password='sua-senha',
    database='mydatabase'
)
```

## 🔒 Arquitetura de Segurança

### Bastion Host com SSM vs SSH Tradicional

| Aspecto | SSH Tradicional | SSM Session Manager |
|---------|----------------|---------------------|
| Porta pública | 22 exposta | Nenhuma |
| Key management | Keys SSH | Não necessário |
| Auditoria | Logs manuais | CloudTrail automático |
| Acesso | IP whitelisting | IAM Policies |
| Rotação de credenciais | Manual | Automática |

### Fluxo de Conexão:

```
Você (Local)
    ↓ (SSM Session Manager)
Bastion Host (EC2)
    ↓ (Rede privada)
RDS Database
```

**Vantagens:**
- ✅ Sem portas SSH públicas
- ✅ Sem gerenciamento de keys
- ✅ Auditoria completa no CloudTrail
- ✅ Controle de acesso via IAM
- ✅ Criptografia end-to-end

## 📊 Endpoints da API

### Listar Instâncias
```
GET /ec2/instances
```

### Criar Bastion Host
```
POST /ec2/instances/bastion
Content-Type: application/json

{
  "name": "bastion-prod",
  "instance_type": "t3.micro",
  "key_name": null,
  "subnet_id": "subnet-xxxxx"
}
```

### Criar Instância Genérica
```
POST /ec2/instances
Content-Type: application/json

{
  "name": "my-instance",
  "ami_id": "ami-xxxxx",
  "instance_type": "t3.micro",
  "key_name": "my-key"
}
```

### Iniciar Instância
```
POST /ec2/instances/{instance_id}/start
```

### Parar Instância
```
POST /ec2/instances/{instance_id}/stop
```

### Terminar Instância
```
DELETE /ec2/instances/{instance_id}/terminate
```

### Obter Comando SSM
```
GET /ec2/instances/{instance_id}/ssm-connection
```

## 💰 Custos

### Bastion Host (t3.micro)
- **Computação**: ~$0.0116/hora = ~$8.50/mês
- **Storage (8 GB)**: ~$0.80/mês
- **Total**: ~$9.30/mês

**Free Tier:**
- 750 horas/mês de t3.micro (12 meses)
- Bastion pode rodar 24/7 gratuitamente no Free Tier!

### SSM Session Manager
- **Gratuito** - sem custos adicionais
- Apenas custos de CloudWatch Logs se habilitado

### Economia vs VPN:
- VPN Site-to-Site: ~$36/mês + $0.05/GB
- Bastion com SSM: ~$9.30/mês (ou grátis no Free Tier)

## 🔒 Permissões AWS Necessárias

### Para EC2
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:RunInstances",
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ec2:TerminateInstances",
        "ec2:DescribeImages",
        "ec2:CreateTags"
      ],
      "Resource": "*"
    }
  ]
}
```

### Para IAM (criar role SSM)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:AttachRolePolicy",
        "iam:CreateInstanceProfile",
        "iam:AddRoleToInstanceProfile",
        "iam:GetRole",
        "iam:GetInstanceProfile"
      ],
      "Resource": [
        "arn:aws:iam::*:role/EC2-SSM-Role",
        "arn:aws:iam::*:instance-profile/EC2-SSM-InstanceProfile"
      ]
    }
  ]
}
```

### Para usar SSM (seu usuário)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:StartSession"
      ],
      "Resource": [
        "arn:aws:ec2:*:*:instance/*",
        "arn:aws:ssm:*:*:document/AWS-StartPortForwardingSessionToRemoteHost",
        "arn:aws:ssm:*:*:document/SSM-SessionManagerRunShell"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "ssm:TerminateSession"
      ],
      "Resource": "arn:aws:ssm:*:*:session/${aws:username}-*"
    }
  ]
}
```

## 🛠️ Configuração Avançada

### Security Group para Bastion

O Bastion **NÃO precisa** de regras de entrada (inbound), apenas saída:

```
Outbound Rules:
- HTTPS (443) → 0.0.0.0/0 (para SSM)
- MySQL (3306) → RDS Security Group
- PostgreSQL (5432) → RDS Security Group
```

### Security Group para RDS

Permita acesso apenas do Bastion:

```
Inbound Rules:
- MySQL (3306) → Bastion Security Group
- PostgreSQL (5432) → Bastion Security Group
```

### Subnet Placement

**Recomendação:**
- Bastion: Subnet privada (mesma do RDS)
- RDS: Subnet privada
- Sem necessidade de subnet pública!

## 💡 Casos de Uso

### 1. Desenvolvimento Local com RDS

```bash
# 1. Crie o túnel
aws ssm start-session --target i-xxxxx \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters host="rds-endpoint",portNumber="3306",localPortNumber="3306"

# 2. Conecte sua aplicação local
DATABASE_URL=mysql://admin:pass@127.0.0.1:3306/mydb
```

### 2. Migrations de Banco

```bash
# Conecte via túnel e execute migrations
alembic upgrade head
# ou
python manage.py migrate
```

### 3. Backup Manual

```bash
# Dump via túnel
mysqldump -h 127.0.0.1 -P 3306 -u admin -p mydatabase > backup.sql
```

### 4. Troubleshooting

```bash
# Conecte ao Bastion
aws ssm start-session --target i-xxxxx

# Teste conectividade
telnet rds-endpoint 3306
nc -zv rds-endpoint 3306
```

## 🐛 Troubleshooting

### Erro: "TargetNotConnected"

**Causa:** SSM Agent não está rodando ou sem permissões

**Solução:**
1. Verifique se a instância tem IAM Role
2. Aguarde 2-3 minutos após criação
3. Reinicie a instância

### Erro: "AccessDenied" ao criar túnel

**Causa:** Falta permissão SSM

**Solução:**
Adicione a policy SSM ao seu usuário IAM

### Túnel fecha imediatamente

**Causa:** Security Group ou Network ACL bloqueando

**Solução:**
1. Verifique Security Group do Bastion (outbound 3306/5432)
2. Verifique Security Group do RDS (inbound do Bastion)
3. Verifique Network ACLs

### Não consigo conectar ao RDS

**Causa:** Endpoint ou porta incorretos

**Solução:**
1. Verifique o endpoint no console RDS
2. Confirme a porta (3306=MySQL, 5432=PostgreSQL)
3. Teste conectividade do Bastion: `telnet rds-endpoint 3306`

## 📚 Recursos Adicionais

- [AWS Systems Manager Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html)
- [Port Forwarding via SSM](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-sessions-start.html#sessions-remote-port-forwarding)
- [Bastion Host Best Practices](https://aws.amazon.com/quickstart/architecture/linux-bastion/)
- [EC2 Instance Types](https://aws.amazon.com/ec2/instance-types/)

## 🎯 Próximas Funcionalidades (Roadmap)

- [ ] Criar Security Groups automaticamente
- [ ] Configurar Session Manager logging
- [ ] Suporte a múltiplos túneis simultâneos
- [ ] Auto Scaling para Bastions
- [ ] Integração com AWS CloudWatch
- [ ] Scripts de conexão automática
- [ ] Suporte a outros bancos (Oracle, SQL Server)

## ✅ Checklist de Segurança

Antes de usar em produção:

- [ ] Bastion em subnet privada
- [ ] RDS em subnet privada
- [ ] Security Groups configurados corretamente
- [ ] IAM Policies com least privilege
- [ ] CloudTrail habilitado
- [ ] Session Manager logging habilitado
- [ ] Instância com patches atualizados
- [ ] Backup do RDS configurado
- [ ] Monitoring com CloudWatch
- [ ] Alertas configurados
