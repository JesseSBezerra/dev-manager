# 📦 Como Instalar o Session Manager Plugin

## ❌ Erro Comum

```
SessionManagerPlugin is not found. Please refer to SessionManager Documentation
```

Este erro significa que o **AWS Session Manager Plugin** não está instalado no seu computador.

## ✅ Solução: Instalar o Plugin

### Windows

#### Opção 1: Download Direto (Recomendado)

1. **Baixe o instalador:**
   ```
   https://s3.amazonaws.com/session-manager-downloads/plugin/latest/windows/SessionManagerPluginSetup.exe
   ```

2. **Execute o instalador** (duplo clique)

3. **Siga o assistente** de instalação

4. **Reinicie o terminal** (PowerShell ou CMD)

5. **Verifique a instalação:**
   ```powershell
   session-manager-plugin
   ```

#### Opção 2: Via PowerShell

```powershell
# Download
Invoke-WebRequest -Uri "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/windows/SessionManagerPluginSetup.exe" -OutFile "$env:TEMP\SessionManagerPluginSetup.exe"

# Instalar
Start-Process -FilePath "$env:TEMP\SessionManagerPluginSetup.exe" -Wait

# Verificar
session-manager-plugin
```

### Linux (Ubuntu/Debian)

```bash
# Download
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "session-manager-plugin.deb"

# Instalar
sudo dpkg -i session-manager-plugin.deb

# Verificar
session-manager-plugin
```

### Linux (Amazon Linux/CentOS/RHEL)

```bash
# Download
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/linux_64bit/session-manager-plugin.rpm" -o "session-manager-plugin.rpm"

# Instalar
sudo yum install -y session-manager-plugin.rpm

# Verificar
session-manager-plugin
```

### macOS

#### Opção 1: Homebrew (Recomendado)

```bash
brew install --cask session-manager-plugin
```

#### Opção 2: Download Manual

```bash
# Download
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/mac/sessionmanager-bundle.zip" -o "sessionmanager-bundle.zip"

# Extrair
unzip sessionmanager-bundle.zip

# Instalar
sudo ./sessionmanager-bundle/install -i /usr/local/sessionmanagerplugin -b /usr/local/bin/session-manager-plugin

# Verificar
session-manager-plugin
```

## ✅ Verificar Instalação

Após instalar, execute no terminal:

```bash
session-manager-plugin
```

**Saída esperada:**
```
The Session Manager plugin is installed successfully. Use the AWS CLI to start a session.
```

## 🔧 Pré-requisitos

Antes de instalar o Session Manager Plugin, você também precisa:

### 1. AWS CLI

**Verificar se está instalado:**
```bash
aws --version
```

**Se não estiver instalado:**

**Windows:**
```powershell
# Download e instale:
https://awscli.amazonaws.com/AWSCLIV2.msi
```

**Linux:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

**macOS:**
```bash
brew install awscli
```

### 2. Credenciais AWS Configuradas

```bash
# Verificar
aws sts get-caller-identity

# Se não configurado, configure:
aws configure
```

## 🚀 Testar Conexão SSM

Após instalar tudo, teste a conexão:

```bash
# Listar instâncias gerenciadas pelo SSM
aws ssm describe-instance-information

# Conectar a uma instância (substitua i-xxxxx)
aws ssm start-session --target i-xxxxxxxxxxxxx
```

## 🔍 Troubleshooting

### Erro: "command not found: session-manager-plugin"

**Causa:** Plugin não está no PATH

**Solução Windows:**
1. Feche e abra o terminal novamente
2. Ou adicione manualmente ao PATH:
   ```
   C:\Program Files\Amazon\SessionManagerPlugin\bin
   ```

**Solução Linux/Mac:**
```bash
# Verificar localização
which session-manager-plugin

# Se não encontrar, reinstale
```

### Erro: "aws: command not found"

**Causa:** AWS CLI não instalado

**Solução:** Instale o AWS CLI primeiro (veja seção Pré-requisitos)

### Erro: "Unable to locate credentials"

**Causa:** AWS não configurado

**Solução:**
```bash
aws configure
# Digite:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (ex: sa-east-1)
# - Default output format (json)
```

### Erro ao conectar: "TargetNotConnected"

**Causa:** Instância não tem IAM Role ou SSM Agent não está rodando

**Solução:**
1. Verifique se a instância tem IAM Role com policy `AmazonSSMManagedInstanceCore`
2. Aguarde 2-3 minutos após criar a instância
3. Verifique se aparece no Systems Manager:
   ```bash
   aws ssm describe-instance-information
   ```

## 📚 Links Úteis

- [Documentação Oficial AWS](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html)
- [AWS CLI Installation](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [Session Manager Prerequisites](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-prerequisites.html)

## ✅ Checklist Completo

Antes de usar o SQL Query Tool:

- [ ] AWS CLI instalado (`aws --version`)
- [ ] Session Manager Plugin instalado (`session-manager-plugin`)
- [ ] Credenciais AWS configuradas (`aws sts get-caller-identity`)
- [ ] Bastion Host criado e rodando
- [ ] Bastion tem IAM Role com SSM
- [ ] RDS criado e disponível
- [ ] Security Groups configurados

## 🎯 Próximo Passo

Após instalar tudo:

1. **Acesse a aplicação:**
   ```
   http://localhost:5000/db-query
   ```

2. **Clique em "Criar Túnel SSM"**

3. **Selecione:**
   - Bastion Host (da lista)
   - Instância RDS (da lista)

4. **Clique em "Criar Túnel"**

5. **Execute suas queries SQL!**

---

**Agora você está pronto para usar o SQL Query Tool!** 🚀
