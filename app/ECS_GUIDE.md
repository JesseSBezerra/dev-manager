# 🐳 Guia de Uso - ECS (Elastic Container Service)

## 📋 Visão Geral

O módulo ECS permite visualizar e monitorar seus clusters, serviços e tasks do Amazon Elastic Container Service através de uma interface web intuitiva.

## 🎯 Funcionalidades

### ✅ Listar Clusters
- Visualize todos os clusters ECS da sua região
- Veja métricas em tempo real:
  - Número de serviços ativos
  - Tasks em execução
  - Tasks pendentes
  - Instâncias registradas

### ✅ Listar Serviços
- Selecione um cluster para ver seus serviços
- Informações exibidas:
  - Nome do serviço
  - Status (ACTIVE, DRAINING, etc.)
  - Launch Type (EC2, FARGATE)
  - Desired Count vs Running Count
  - Task Definition utilizada
  - Load Balancers associados

### ✅ Listar Tasks
- Visualize todas as tasks em execução
- Detalhes incluem:
  - Task ID
  - Status atual
  - CPU e Memory alocados
  - Número de containers
  - Health status

### 🆕 Gerenciar Serviços

#### ⏸️ Parar Serviço
- Para um serviço ECS (define desiredCount = 0)
- Todas as tasks serão encerradas
- Útil para economizar custos em ambientes de desenvolvimento

#### ▶️ Iniciar Serviço
- Inicia um serviço parado
- Define o número desejado de tasks (1-100)
- As tasks serão iniciadas automaticamente

#### 🔄 Mudar Capacity Provider
- Alterna entre FARGATE e FARGATE_SPOT
- **FARGATE**: Preço normal, maior disponibilidade
- **FARGATE_SPOT**: Até 70% mais barato, pode ser interrompido
- Força um novo deployment para aplicar as mudanças

## 🚀 Como Usar

### 1. Acessar o Módulo ECS

```
http://localhost:5000/ecs
```

Ou clique em **"ECS"** no menu de navegação.

### 2. Visualizar Clusters

A página inicial carrega automaticamente todos os clusters da região configurada.

**Cada card de cluster mostra:**
- Nome do cluster
- Status (ACTIVE, INACTIVE)
- Métricas principais

**Clique em um cluster** para ver seus serviços.

### 3. Visualizar Serviços

Após selecionar um cluster, você verá uma tabela com todos os serviços:

| Coluna | Descrição |
|--------|-----------|
| Nome do Serviço | Nome identificador do serviço |
| Status | Estado atual (ACTIVE, DRAINING, etc.) |
| Launch Type | EC2 ou FARGATE |
| Desired | Número desejado de tasks |
| Running | Tasks atualmente em execução |
| Pending | Tasks aguardando inicialização |
| Task Definition | Versão da task definition |

**Badges coloridos:**
- 🟢 Verde: Serviço saudável (running = desired)
- 🟡 Amarelo: Serviço em ajuste (running ≠ desired)

### 4. Visualizar Tasks

Clique no botão **"Ver Tasks"** para listar todas as tasks do cluster.

**Informações exibidas:**
- Task ID (primeiros 12 caracteres)
- Status (RUNNING, PENDING, STOPPED)
- Launch Type
- Task Definition
- Recursos (CPU/Memory)
- Número de containers
- Health Status

## 📊 Endpoints da API

### Listar Clusters
```
GET /ecs/clusters
```

**Resposta:**
```json
{
  "success": true,
  "clusters": [
    {
      "name": "production-cluster",
      "status": "ACTIVE",
      "running_tasks": 10,
      "pending_tasks": 0,
      "active_services": 5
    }
  ],
  "count": 1
}
```

### Listar Serviços de um Cluster
```
GET /ecs/clusters/{cluster_name}/services
```

**Resposta:**
```json
{
  "success": true,
  "services": [
    {
      "name": "api-service",
      "status": "ACTIVE",
      "desired_count": 3,
      "running_count": 3,
      "launch_type": "FARGATE"
    }
  ],
  "count": 1,
  "cluster": "production-cluster"
}
```

### Listar Tasks de um Cluster
```
GET /ecs/clusters/{cluster_name}/tasks
```

**Query Parameters:**
- `service_name` (opcional): Filtrar tasks por serviço

**Resposta:**
```json
{
  "success": true,
  "tasks": [
    {
      "task_id": "abc123def456",
      "status": "RUNNING",
      "launch_type": "FARGATE",
      "cpu": "256",
      "memory": "512"
    }
  ],
  "count": 1
}
```

## 🔧 Exemplos de Uso via API

### Python (requests)

```python
import requests

BASE_URL = "http://localhost:5000"

# Listar clusters
response = requests.get(f"{BASE_URL}/ecs/clusters")
clusters = response.json()

# Listar serviços de um cluster
cluster_name = "production-cluster"
response = requests.get(f"{BASE_URL}/ecs/clusters/{cluster_name}/services")
services = response.json()

# Listar tasks
response = requests.get(f"{BASE_URL}/ecs/clusters/{cluster_name}/tasks")
tasks = response.json()
```

### cURL

```bash
# Listar clusters
curl http://localhost:5000/ecs/clusters

# Listar serviços
curl http://localhost:5000/ecs/clusters/production-cluster/services

# Listar tasks
curl http://localhost:5000/ecs/clusters/production-cluster/tasks

# Listar tasks de um serviço específico
curl "http://localhost:5000/ecs/clusters/production-cluster/tasks?service_name=api-service"
```

## 🎨 Interface

### Cores e Status

**Clusters:**
- 🟢 Verde (ACTIVE): Cluster ativo e operacional
- 🟡 Amarelo (outros): Cluster em outro estado

**Serviços:**
- 🟢 Verde: Serviço saudável (running = desired)
- 🟡 Amarelo: Serviço ajustando (running ≠ desired)

**Tasks:**
- 🟢 Verde (RUNNING): Task em execução
- 🟡 Amarelo (PENDING): Task iniciando
- 🔴 Vermelho (STOPPED): Task parada

**Health Status:**
- 🟢 HEALTHY: Container saudável
- 🔴 UNHEALTHY: Container com problemas
- ⚪ UNKNOWN: Status desconhecido

## 🔒 Permissões AWS Necessárias

Sua conta AWS precisa das seguintes permissões:

### Permissões de Leitura (Obrigatórias)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecs:ListClusters",
        "ecs:DescribeClusters",
        "ecs:ListServices",
        "ecs:DescribeServices",
        "ecs:ListTasks",
        "ecs:DescribeTasks"
      ],
      "Resource": "*"
    }
  ]
}
```

### Permissões de Escrita (Para Gerenciar Serviços)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecs:UpdateService"
      ],
      "Resource": "arn:aws:ecs:*:*:service/*"
    }
  ]
}
```

**Nota:** A permissão `ecs:UpdateService` é necessária para:
- Parar serviços
- Iniciar serviços
- Mudar Capacity Provider

### 5. Gerenciar Serviços

Na tabela de serviços, você verá botões de ação para cada serviço:

**Botões disponíveis:**
- 🛑 **Parar** (vermelho): Para o serviço (desiredCount = 0)
- ▶️ **Iniciar** (verde): Inicia o serviço (aparece quando parado)
- 🔄 **Mudar Capacity** (amarelo): Alterna entre FARGATE e FARGATE_SPOT
- ℹ️ **Detalhes** (azul): Visualiza informações do serviço

**Exemplo de uso:**

1. **Para parar um serviço:**
   - Clique no botão 🛑 (vermelho)
   - Confirme a ação
   - Aguarde 2 segundos para ver a atualização

2. **Para iniciar um serviço:**
   - Clique no botão ▶️ (verde)
   - Digite o número de tasks desejado (ex: 2)
   - Confirme

3. **Para mudar de FARGATE para FARGATE_SPOT:**
   - Clique no botão 🔄 (amarelo)
   - Confirme a mudança
   - Aguarde o deployment (pode levar alguns minutos)

## ⚠️ Limitações Atuais

- **Região única**: Mostra apenas recursos da região configurada no `.env`
- **Sem filtros avançados**: Filtros limitados aos disponíveis na API
- **Capacity Providers**: Apenas FARGATE e FARGATE_SPOT são suportados

## 🔄 Atualizações em Tempo Real

A interface **não** atualiza automaticamente. Use os botões **"Atualizar"** para recarregar os dados:

- **Atualizar Clusters**: Recarrega lista de clusters
- **Atualizar Serviços**: Recarrega serviços do cluster selecionado

## 💡 Dicas

1. **Monitoramento**: Use a página ECS para monitorar o status dos seus serviços
2. **Troubleshooting**: Verifique tasks com status PENDING ou STOPPED
3. **Capacidade**: Monitore running_count vs desired_count para identificar problemas
4. **Health Checks**: Fique atento ao health_status das tasks

## 🐛 Troubleshooting

### Nenhum cluster encontrado
- Verifique se você tem clusters ECS na região configurada
- Confirme as permissões AWS

### Erro ao listar serviços
- Verifique se o cluster existe
- Confirme o nome do cluster (case-sensitive)

### Tasks não aparecem
- Alguns clusters podem não ter tasks em execução
- Verifique se há serviços ativos no cluster

## 📚 Recursos Adicionais

- [Documentação AWS ECS](https://docs.aws.amazon.com/ecs/)
- [boto3 ECS Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecs.html)
- [ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)

## 🎯 Próximas Funcionalidades (Roadmap)

- [ ] Atualização automática (polling)
- [ ] Filtros avançados
- [ ] Visualização de logs dos containers
- [ ] Métricas de CloudWatch integradas
- [ ] Suporte a múltiplas regiões
- [ ] Ações de gerenciamento (start/stop tasks)
