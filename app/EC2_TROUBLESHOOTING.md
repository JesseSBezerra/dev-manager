# 🔧 Troubleshooting - EC2 e Bastion Host

## ❌ Erro: "Invalid IAM Instance Profile name"

### Causa
O Instance Profile não existe ou não foi propagado corretamente no IAM.

### Soluções

#### Solução 1: Executar script de criação manual

```bash
python create_ssm_role.py
```

Este script irá:
- Criar a role `EC2-SSM-Role`
- Anexar a policy `AmazonSSMManagedInstanceCore`
- Criar o instance profile `EC2-SSM-InstanceProfile`
- Aguardar propagação (10 segundos)

#### Solução 2: Criar manualmente no Console AWS

1. Acesse **IAM** → **Roles** → **Create role**
2. Selecione **AWS service** → **EC2**
3. Anexe a policy: `AmazonSSMManagedInstanceCore`
4. Nome da role: `EC2-SSM-Role`
5. Crie a role
6. Aguarde 1-2 minutos para propagação

#### Solução 3: Criar sem IAM Role

Se você não tem permissões IAM, pode criar o Bastion sem a role:

1. A aplicação criará a instância sem IAM Role
2. Você verá uma mensagem: "Instância criada SEM IAM Role"
3. Depois, anexe manualmente:
   - Console EC2 → Instância → Actions → Security → Modify IAM role
   - Selecione `EC2-SSM-InstanceProfile`

#### Solução 4: Usar AWS CLI

```bash
# Criar role
aws iam create-role \
  --role-name EC2-SSM-Role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ec2.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Anexar policy
aws iam attach-role-policy \
  --role-name EC2-SSM-Role \
  --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

# Criar instance profile
aws iam create-instance-profile \
  --instance-profile-name EC2-SSM-InstanceProfile

# Adicionar role ao profile
aws iam add-role-to-instance-profile \
  --instance-profile-name EC2-SSM-InstanceProfile \
  --role-name EC2-SSM-Role

# Aguardar propagação
sleep 10
```

---

## ❌ Erro: "AccessDenied" ao criar IAM Role

### Causa
Seu usuário IAM não tem permissões para criar roles.

### Solução

Peça ao administrador AWS para adicionar estas permissões ao seu usuário:

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

**Alternativa:** Peça ao administrador para criar a role manualmente e você poderá usar.

---

## ❌ Erro: "TargetNotConnected" ao conectar via SSM

### Causa
A instância não está registrada no SSM ou o SSM Agent não está rodando.

### Soluções

#### 1. Verificar IAM Role
```bash
# Verifique se a instância tem IAM Role
aws ec2 describe-instances --instance-ids i-xxxxx \
  --query 'Reservations[0].Instances[0].IamInstanceProfile'
```

Se não tiver, anexe:
```bash
aws ec2 associate-iam-instance-profile \
  --instance-id i-xxxxx \
  --iam-instance-profile Name=EC2-SSM-InstanceProfile
```

#### 2. Verificar SSM Agent
Conecte via SSH (se tiver key pair) e verifique:
```bash
sudo systemctl status amazon-ssm-agent
sudo systemctl start amazon-ssm-agent
```

#### 3. Aguardar registro
Após anexar a role, aguarde 2-3 minutos para o SSM Agent registrar a instância.

Verifique se aparece no Systems Manager:
```bash
aws ssm describe-instance-information \
  --filters "Key=InstanceIds,Values=i-xxxxx"
```

---

## ❌ Erro: "No AMI found" ao criar Bastion

### Causa
Região não tem AMI do Amazon Linux 2 ou filtro incorreto.

### Solução

Busque AMIs disponíveis:
```bash
aws ec2 describe-images \
  --owners amazon \
  --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" \
  --query 'Images[0].ImageId' \
  --output text
```

Ou use uma AMI específica da sua região:
- sa-east-1: ami-0c820c196a818d66a
- us-east-1: ami-0c55b159cbfafe1f0

---

## ❌ Erro: "InvalidParameterValue" ao criar instância

### Causa
Parâmetros inválidos (subnet, security group, etc.)

### Soluções

#### Verificar Subnet
```bash
aws ec2 describe-subnets --subnet-ids subnet-xxxxx
```

#### Verificar Security Group
```bash
aws ec2 describe-security-groups --group-ids sg-xxxxx
```

#### Verificar VPC
Certifique-se de que subnet e security group estão na mesma VPC.

---

## ❌ Túnel SSM fecha imediatamente

### Causa
Security Group bloqueando conexão do Bastion ao RDS.

### Solução

#### 1. Security Group do Bastion (Outbound)
Deve permitir saída para:
- HTTPS (443) → 0.0.0.0/0 (para SSM)
- MySQL (3306) → RDS Security Group
- PostgreSQL (5432) → RDS Security Group

```bash
aws ec2 authorize-security-group-egress \
  --group-id sg-bastion \
  --protocol tcp \
  --port 3306 \
  --source-group sg-rds
```

#### 2. Security Group do RDS (Inbound)
Deve permitir entrada de:
- MySQL (3306) ← Bastion Security Group
- PostgreSQL (5432) ← Bastion Security Group

```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-rds \
  --protocol tcp \
  --port 3306 \
  --source-group sg-bastion
```

#### 3. Testar conectividade
Conecte ao Bastion e teste:
```bash
aws ssm start-session --target i-xxxxx

# Dentro do Bastion:
telnet rds-endpoint.sa-east-1.rds.amazonaws.com 3306
nc -zv rds-endpoint.sa-east-1.rds.amazonaws.com 3306
```

---

## ❌ Erro: "Session Manager plugin not found"

### Causa
Plugin do Session Manager não está instalado.

### Solução

#### Windows
```powershell
# Download:
https://s3.amazonaws.com/session-manager-downloads/plugin/latest/windows/SessionManagerPluginSetup.exe

# Instale e reinicie o terminal
```

#### Linux (Ubuntu/Debian)
```bash
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "session-manager-plugin.deb"
sudo dpkg -i session-manager-plugin.deb
```

#### Mac
```bash
brew install --cask session-manager-plugin
```

#### Verificar instalação
```bash
session-manager-plugin --version
```

---

## ❌ Instância não inicia

### Causa
Problemas com AMI, subnet, ou limites de conta.

### Soluções

#### 1. Verificar limites
```bash
aws service-quotas get-service-quota \
  --service-code ec2 \
  --quota-code L-1216C47A
```

#### 2. Verificar eventos da instância
```bash
aws ec2 describe-instance-status \
  --instance-ids i-xxxxx \
  --include-all-instances
```

#### 3. Ver logs do sistema
No console EC2 → Instância → Actions → Monitor and troubleshoot → Get system log

---

## ❌ Não consigo conectar ao RDS via túnel

### Causa
Endpoint, porta ou credenciais incorretas.

### Soluções

#### 1. Verificar endpoint do RDS
```bash
aws rds describe-db-instances \
  --db-instance-identifier seu-rds \
  --query 'DBInstances[0].Endpoint'
```

#### 2. Verificar porta
- MySQL/MariaDB: 3306
- PostgreSQL: 5432
- Oracle: 1521
- SQL Server: 1433

#### 3. Testar túnel
```bash
# Criar túnel
aws ssm start-session --target i-xxxxx \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters host="rds-endpoint",portNumber="3306",localPortNumber="3306"

# Em outro terminal, testar
telnet localhost 3306
```

#### 4. Verificar credenciais
Certifique-se de usar o usuário e senha corretos do RDS.

---

## 💡 Dicas de Prevenção

### 1. Sempre aguarde propagação
Após criar IAM Roles, aguarde 10-15 segundos antes de usar.

### 2. Use tags
Sempre adicione tags às instâncias para organização:
```
Name: bastion-prod
Environment: production
ManagedBy: AWSManager
```

### 3. Security Groups
Configure antes de criar instâncias:
- Bastion: Apenas outbound necessário
- RDS: Apenas inbound do Bastion

### 4. Subnet placement
- Bastion: Subnet privada (mesma do RDS)
- Não precisa de subnet pública!

### 5. Monitore custos
- Pare instâncias quando não usar
- Use t3.micro para Bastion (Free Tier)
- Configure alertas de billing

---

## 📞 Suporte

Se o problema persistir:

1. **Verifique logs da aplicação Flask**
2. **Execute**: `python check_aws_credentials.py`
3. **Execute**: `python create_ssm_role.py`
4. **Verifique CloudTrail** para erros de API
5. **Consulte documentação AWS**:
   - [SSM Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html)
   - [EC2 Troubleshooting](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-troubleshoot.html)

---

## ✅ Checklist de Verificação

Antes de criar um Bastion Host:

- [ ] IAM Role `EC2-SSM-Role` existe
- [ ] Instance Profile `EC2-SSM-InstanceProfile` existe
- [ ] Você tem permissões EC2 e IAM
- [ ] AWS CLI configurado
- [ ] Session Manager plugin instalado
- [ ] Security Groups configurados
- [ ] Subnet selecionada (opcional)
- [ ] RDS já criado (se for usar túnel)

Após criar o Bastion:

- [ ] Instância está "running"
- [ ] IAM Role anexada
- [ ] Aparece no Systems Manager (2-3 min)
- [ ] Consegue conectar via SSM
- [ ] Consegue criar túnel para RDS
- [ ] Consegue conectar ao RDS via localhost
