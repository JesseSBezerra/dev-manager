// JavaScript para SQS & SNS

const alertContainer = document.getElementById('alertContainer');
let currentQueueUrl = null;
let currentTopicArn = null;
let allQueues = [];
let allTopics = [];

// Event Listeners
document.getElementById('refreshQueuesBtn').addEventListener('click', loadQueues);
document.getElementById('refreshTopicsBtn').addEventListener('click', loadTopics);
document.getElementById('createQueueBtn').addEventListener('click', createQueue);
document.getElementById('createTopicBtn').addEventListener('click', createTopic);
document.getElementById('sqsFilter').addEventListener('input', filterQueues);
document.getElementById('snsFilter').addEventListener('input', filterTopics);

// Carregar ao iniciar
document.addEventListener('DOMContentLoaded', () => {
    loadQueues();
    loadTopics();
});

/**
 * Exibe alerta
 */
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    
    alertDiv.innerHTML = `
        <strong>${type === 'success' ? '✅' : type === 'danger' ? '❌' : 'ℹ️'}</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// ==================== SQS ====================

/**
 * Carrega filas SQS
 */
async function loadQueues() {
    const container = document.getElementById('queuesContainer');
    container.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2">Carregando filas...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/messaging/sqs/queues');
        const result = await response.json();
        
        if (result.success) {
            allQueues = result.queues;
            displayQueues(allQueues);
        } else {
            container.innerHTML = `<div class="alert alert-danger">${result.message}</div>`;
        }
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">Erro: ${error.message}</div>`;
    }
}

/**
 * Exibe filas
 */
function displayQueues(queues) {
    const container = document.getElementById('queuesContainer');
    
    if (queues.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted">
                <i class="bi bi-inbox" style="font-size: 3rem;"></i>
                <p class="mt-2">Nenhuma fila encontrada</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="table-responsive"><table class="table table-hover">';
    html += `
        <thead class="table-dark">
            <tr>
                <th>Nome</th>
                <th>Tipo</th>
                <th>Mensagens</th>
                <th>Em Processamento</th>
                <th>Atrasadas</th>
                <th>Ações</th>
            </tr>
        </thead>
        <tbody>
    `;
    
    queues.forEach(queue => {
        const totalMessages = queue.messages_available + queue.messages_in_flight + queue.messages_delayed;
        const badgeColor = totalMessages > 0 ? 'danger' : 'secondary';
        
        html += `
            <tr>
                <td>
                    <strong>${queue.name}</strong>
                    ${queue.is_fifo ? '<span class="badge bg-info ms-2">FIFO</span>' : ''}
                </td>
                <td>${queue.is_fifo ? 'FIFO' : 'Standard'}</td>
                <td><span class="badge bg-${badgeColor}">${queue.messages_available}</span></td>
                <td><span class="badge bg-warning">${queue.messages_in_flight}</span></td>
                <td><span class="badge bg-info">${queue.messages_delayed}</span></td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="viewQueueMessages('${queue.url}', '${queue.name}')" title="Ver Mensagens">
                        <i class="bi bi-envelope"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteQueue('${queue.url}', '${queue.name}')" title="Deletar">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html;
}

/**
 * Filtra filas
 */
function filterQueues() {
    const filter = document.getElementById('sqsFilter').value.toLowerCase();
    const filtered = allQueues.filter(q => q.name.toLowerCase().includes(filter));
    displayQueues(filtered);
}

/**
 * Cria fila
 */
async function createQueue() {
    const name = document.getElementById('queueName').value.trim();
    const isFifo = document.getElementById('queueFifo').checked;
    const delay = parseInt(document.getElementById('queueDelay').value);
    const retention = parseInt(document.getElementById('queueRetention').value);
    const visibility = parseInt(document.getElementById('queueVisibility').value);
    
    if (!name) {
        showAlert('Nome da fila é obrigatório', 'warning');
        return;
    }
    
    const btn = document.getElementById('createQueueBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Criando...';
    
    try {
        const response = await fetch('/messaging/sqs/queues', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                queue_name: name,
                is_fifo: isFifo,
                delay_seconds: delay,
                message_retention_period: retention,
                visibility_timeout: visibility
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('createQueueModal')).hide();
            document.getElementById('queueName').value = '';
            document.getElementById('queueFifo').checked = false;
            loadQueues();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-plus-circle"></i> Criar';
    }
}

/**
 * Deleta fila
 */
async function deleteQueue(queueUrl, queueName) {
    if (!confirm(`Tem certeza que deseja deletar a fila "${queueName}"?`)) {
        return;
    }
    
    try {
        const response = await fetch('/messaging/sqs/queues', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ queue_url: queueUrl })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            loadQueues();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

/**
 * Visualiza mensagens da fila
 */
function viewQueueMessages(queueUrl, queueName) {
    currentQueueUrl = queueUrl;
    document.getElementById('queueMessagesTitle').textContent = queueName;
    document.getElementById('messagesContent').innerHTML = '<p class="text-muted">Clique em "Receber Mensagens" para visualizar</p>';
    
    // Configura event listeners
    document.getElementById('receiveMessagesBtn').onclick = () => receiveMessages(queueUrl);
    document.getElementById('sendMessageBtn').onclick = () => sendMessage(queueUrl);
    document.getElementById('purgeQueueBtn').onclick = () => purgeQueue(queueUrl, queueName);
    
    new bootstrap.Modal(document.getElementById('queueMessagesModal')).show();
}

/**
 * Recebe mensagens
 */
async function receiveMessages(queueUrl) {
    const container = document.getElementById('messagesContent');
    container.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2">Recebendo mensagens...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/messaging/sqs/messages/receive', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ queue_url: queueUrl, max_messages: 10 })
        });
        
        const result = await response.json();
        
        if (result.success) {
            if (result.messages.length === 0) {
                container.innerHTML = '<div class="alert alert-info">Nenhuma mensagem disponível</div>';
            } else {
                displayMessages(result.messages, queueUrl);
            }
        } else {
            container.innerHTML = `<div class="alert alert-danger">${result.message}</div>`;
        }
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">Erro: ${error.message}</div>`;
    }
}

/**
 * Exibe mensagens
 */
function displayMessages(messages, queueUrl) {
    const container = document.getElementById('messagesContent');
    
    let html = `<p class="text-muted">${messages.length} mensagem(ns) recebida(s)</p>`;
    
    messages.forEach((msg, index) => {
        html += `
            <div class="card mb-2">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <span><strong>Mensagem ${index + 1}</strong></span>
                    <button class="btn btn-sm btn-danger" onclick="deleteMessage('${queueUrl}', '${msg.ReceiptHandle}')">
                        <i class="bi bi-trash"></i> Deletar
                    </button>
                </div>
                <div class="card-body">
                    <p><strong>ID:</strong> ${msg.MessageId}</p>
                    <p><strong>Corpo:</strong></p>
                    <pre class="bg-light p-2 rounded">${msg.Body}</pre>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

/**
 * Envia mensagem
 */
async function sendMessage(queueUrl) {
    const body = document.getElementById('messageBody').value.trim();
    const delay = parseInt(document.getElementById('messageDelay').value);
    
    if (!body) {
        showAlert('Mensagem é obrigatória', 'warning');
        return;
    }
    
    const btn = document.getElementById('sendMessageBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Enviando...';
    
    try {
        const response = await fetch('/messaging/sqs/messages/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                queue_url: queueUrl,
                message_body: body,
                delay_seconds: delay
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('sendMessageModal')).hide();
            document.getElementById('messageBody').value = '';
            document.getElementById('messageDelay').value = '0';
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-send"></i> Enviar';
    }
}

/**
 * Deleta mensagem
 */
async function deleteMessage(queueUrl, receiptHandle) {
    try {
        const response = await fetch('/messaging/sqs/messages', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                queue_url: queueUrl,
                receipt_handle: receiptHandle
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            receiveMessages(queueUrl);
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

/**
 * Limpa fila
 */
async function purgeQueue(queueUrl, queueName) {
    if (!confirm(`Tem certeza que deseja limpar TODAS as mensagens da fila "${queueName}"?`)) {
        return;
    }
    
    try {
        const response = await fetch('/messaging/sqs/queues/purge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ queue_url: queueUrl })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            document.getElementById('messagesContent').innerHTML = '<div class="alert alert-success">Fila limpa com sucesso!</div>';
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

// ==================== SNS ====================

/**
 * Carrega tópicos SNS
 */
async function loadTopics() {
    const container = document.getElementById('topicsContainer');
    container.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-success" role="status"></div>
            <p class="mt-2">Carregando tópicos...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/messaging/sns/topics');
        const result = await response.json();
        
        if (result.success) {
            allTopics = result.topics;
            displayTopics(allTopics);
        } else {
            container.innerHTML = `<div class="alert alert-danger">${result.message}</div>`;
        }
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">Erro: ${error.message}</div>`;
    }
}

/**
 * Exibe tópicos
 */
function displayTopics(topics) {
    const container = document.getElementById('topicsContainer');
    
    if (topics.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted">
                <i class="bi bi-megaphone" style="font-size: 3rem;"></i>
                <p class="mt-2">Nenhum tópico encontrado</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="table-responsive"><table class="table table-hover">';
    html += `
        <thead class="table-dark">
            <tr>
                <th>Nome</th>
                <th>Tipo</th>
                <th>Inscrições</th>
                <th>Ações</th>
            </tr>
        </thead>
        <tbody>
    `;
    
    topics.forEach(topic => {
        html += `
            <tr>
                <td>
                    <strong>${topic.name}</strong>
                    ${topic.is_fifo ? '<span class="badge bg-info ms-2">FIFO</span>' : ''}
                    ${topic.display_name ? `<br><small class="text-muted">${topic.display_name}</small>` : ''}
                </td>
                <td>${topic.is_fifo ? 'FIFO' : 'Standard'}</td>
                <td>
                    <span class="badge bg-success">${topic.subscriptions_confirmed}</span>
                    ${topic.subscriptions_pending > 0 ? `<span class="badge bg-warning">${topic.subscriptions_pending} pendente(s)</span>` : ''}
                </td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="publishToTopic('${topic.arn}', '${topic.name}')" title="Publicar">
                        <i class="bi bi-megaphone"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteTopic('${topic.arn}', '${topic.name}')" title="Deletar">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html;
}

/**
 * Filtra tópicos
 */
function filterTopics() {
    const filter = document.getElementById('snsFilter').value.toLowerCase();
    const filtered = allTopics.filter(t => t.name.toLowerCase().includes(filter));
    displayTopics(filtered);
}

/**
 * Cria tópico
 */
async function createTopic() {
    const name = document.getElementById('topicName').value.trim();
    const displayName = document.getElementById('topicDisplayName').value.trim();
    const isFifo = document.getElementById('topicFifo').checked;
    
    if (!name) {
        showAlert('Nome do tópico é obrigatório', 'warning');
        return;
    }
    
    const btn = document.getElementById('createTopicBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Criando...';
    
    try {
        const response = await fetch('/messaging/sns/topics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic_name: name,
                display_name: displayName,
                is_fifo: isFifo
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('createTopicModal')).hide();
            document.getElementById('topicName').value = '';
            document.getElementById('topicDisplayName').value = '';
            document.getElementById('topicFifo').checked = false;
            loadTopics();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-plus-circle"></i> Criar';
    }
}

/**
 * Deleta tópico
 */
async function deleteTopic(topicArn, topicName) {
    if (!confirm(`Tem certeza que deseja deletar o tópico "${topicName}"?`)) {
        return;
    }
    
    try {
        const response = await fetch('/messaging/sns/topics', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic_arn: topicArn })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            loadTopics();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

/**
 * Publica mensagem em tópico
 */
function publishToTopic(topicArn, topicName) {
    currentTopicArn = topicArn;
    
    document.getElementById('publishMessageBtn').onclick = () => publishMessage(topicArn);
    
    new bootstrap.Modal(document.getElementById('publishMessageModal')).show();
}

/**
 * Publica mensagem
 */
async function publishMessage(topicArn) {
    const subject = document.getElementById('publishSubject').value.trim();
    const message = document.getElementById('publishMessage').value.trim();
    
    if (!message) {
        showAlert('Mensagem é obrigatória', 'warning');
        return;
    }
    
    const btn = document.getElementById('publishMessageBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Publicando...';
    
    try {
        const response = await fetch('/messaging/sns/publish', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic_arn: topicArn,
                message: message,
                subject: subject || null
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('publishMessageModal')).hide();
            document.getElementById('publishSubject').value = '';
            document.getElementById('publishMessage').value = '';
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-megaphone"></i> Publicar';
    }
}
