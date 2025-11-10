// JavaScript para Kafka Catalog

const alertContainer = document.getElementById('alertContainer');
let allOwners = [];
let allAuths = [];
let allSchemas = [];
let allClusters = [];
let currentClusterId = null;
let currentTopicId = null;

// Event Listeners
document.getElementById('refreshOwnersBtn').addEventListener('click', loadOwners);
document.getElementById('refreshAuthBtn').addEventListener('click', loadAuthentications);
document.getElementById('refreshSchemasBtn').addEventListener('click', loadSchemas);
document.getElementById('refreshClustersBtn').addEventListener('click', loadClusters);
document.getElementById('createOwnerBtn').addEventListener('click', createOwner);
document.getElementById('createAuthBtn').addEventListener('click', createAuthentication);
document.getElementById('createSchemaBtn').addEventListener('click', createSchema);
document.getElementById('createClusterBtn').addEventListener('click', createCluster);
document.getElementById('filterOwner').addEventListener('change', filterClusters);
document.getElementById('authType').addEventListener('change', toggleAuthFields);

document.addEventListener('DOMContentLoaded', () => {
    loadOwners();
    loadAuthentications();
    loadSchemas();
    loadClusters();
});

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <strong>${type === 'success' ? '✅' : type === 'danger' ? '❌' : 'ℹ️'}</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    alertContainer.appendChild(alertDiv);
    setTimeout(() => alertDiv.remove(), 5000);
}

function toggleAuthFields() {
    const authType = document.getElementById('authType').value;
    const saslFields = document.getElementById('saslFields');
    const credFields = document.getElementById('credentialsFields');
    
    if (authType === 'SASL_SSL') {
        saslFields.style.display = 'block';
        credFields.style.display = 'block';
    } else if (authType === 'SSL') {
        saslFields.style.display = 'none';
        credFields.style.display = 'none';
    } else {
        saslFields.style.display = 'none';
        credFields.style.display = 'none';
    }
}

// ==================== OWNERS ====================

async function loadOwners() {
    try {
        const response = await fetch('/kafka/owners');
        const result = await response.json();
        
        if (result.success) {
            allOwners = result.owners;
            displayOwners(allOwners);
            populateOwnerSelects();
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

function displayOwners(owners) {
    const container = document.getElementById('ownersContainer');
    
    if (owners.length === 0) {
        container.innerHTML = '<div class="text-center text-muted"><p>Nenhum dono cadastrado</p></div>';
        return;
    }
    
    let html = '<div class="list-group">';
    owners.forEach(owner => {
        html += `
            <div class="list-group-item">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-1">${owner.name}</h6>
                        ${owner.description ? `<small class="text-muted">${owner.description}</small>` : ''}
                    </div>
                    <button class="btn btn-sm btn-danger" onclick="deleteOwner(${owner.id}, '${owner.name}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}

async function createOwner() {
    const name = document.getElementById('ownerName').value.trim();
    const description = document.getElementById('ownerDescription').value.trim();
    
    if (!name) {
        showAlert('Nome é obrigatório', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/kafka/owners', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('createOwnerModal')).hide();
            document.getElementById('ownerName').value = '';
            document.getElementById('ownerDescription').value = '';
            loadOwners();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

async function deleteOwner(ownerId, ownerName) {
    if (!confirm(`Deletar dono "${ownerName}"?`)) return;
    
    try {
        const response = await fetch(`/kafka/owners/${ownerId}`, { method: 'DELETE' });
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            loadOwners();
            loadClusters();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

function populateOwnerSelects() {
    const selects = [
        document.getElementById('authOwner'),
        document.getElementById('schemaOwner'),
        document.getElementById('clusterOwner'),
        document.getElementById('filterOwner')
    ];
    
    selects.forEach(select => {
        if (!select) return;
        const isFilter = select.id === 'filterOwner';
        select.innerHTML = isFilter ? '<option value="">Todos os donos</option>' : '<option value="">Selecione...</option>';
        allOwners.forEach(owner => {
            const option = document.createElement('option');
            option.value = owner.id;
            option.textContent = owner.name;
            select.appendChild(option);
        });
    });
}

// ==================== AUTHENTICATIONS ====================

async function loadAuthentications() {
    try {
        const response = await fetch('/kafka/authentications');
        const result = await response.json();
        
        if (result.success) {
            allAuths = result.authentications;
            displayAuthentications(allAuths);
            populateAuthSelects();
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

function displayAuthentications(auths) {
    const container = document.getElementById('authContainer');
    
    if (auths.length === 0) {
        container.innerHTML = '<div class="text-center text-muted"><p>Nenhuma autenticação cadastrada</p></div>';
        return;
    }
    
    let html = '<div class="list-group">';
    auths.forEach(auth => {
        html += `
            <div class="list-group-item">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-1">${auth.name} <span class="badge bg-primary">${auth.auth_type}</span></h6>
                        <small class="text-muted">Dono: ${auth.owner_name}</small>
                    </div>
                    <button class="btn btn-sm btn-danger" onclick="deleteAuth(${auth.id}, '${auth.name}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}

async function createAuthentication() {
    const name = document.getElementById('authName').value.trim();
    const ownerId = document.getElementById('authOwner').value;
    const authType = document.getElementById('authType').value;
    const saslMechanism = document.getElementById('saslMechanism').value;
    const username = document.getElementById('authUsername').value.trim();
    const password = document.getElementById('authPassword').value.trim();
    
    if (!name || !ownerId || !authType) {
        showAlert('Nome, Dono e Tipo são obrigatórios', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/kafka/authentications', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name, owner_id: ownerId, auth_type: authType,
                sasl_mechanism: saslMechanism, username, password
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('createAuthModal')).hide();
            document.getElementById('authName').value = '';
            document.getElementById('authUsername').value = '';
            document.getElementById('authPassword').value = '';
            loadAuthentications();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

async function deleteAuth(authId, authName) {
    if (!confirm(`Deletar autenticação "${authName}"?`)) return;
    
    try {
        const response = await fetch(`/kafka/authentications/${authId}`, { method: 'DELETE' });
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            loadAuthentications();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

function populateAuthSelects() {
    const select = document.getElementById('clusterAuth');
    if (!select) return;
    
    select.innerHTML = '<option value="">Nenhuma</option>';
    allAuths.forEach(auth => {
        const option = document.createElement('option');
        option.value = auth.id;
        option.textContent = `${auth.name} (${auth.auth_type})`;
        select.appendChild(option);
    });
}

// ==================== SCHEMAS ====================

async function loadSchemas() {
    try {
        const response = await fetch('/kafka/schemas');
        const result = await response.json();
        
        if (result.success) {
            allSchemas = result.schemas;
            displaySchemas(allSchemas);
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

function displaySchemas(schemas) {
    const container = document.getElementById('schemasContainer');
    
    if (schemas.length === 0) {
        container.innerHTML = '<div class="text-center text-muted"><p>Nenhum schema cadastrado</p></div>';
        return;
    }
    
    let html = '';
    schemas.forEach(schema => {
        html += `
            <div class="card mb-2">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <span><strong>${schema.name}</strong> <span class="badge bg-info">${schema.schema_type}</span></span>
                    <button class="btn btn-sm btn-danger" onclick="deleteSchema(${schema.id}, '${schema.name}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
                <div class="card-body">
                    <p class="mb-1"><strong>Dono:</strong> ${schema.owner_name}</p>
                    ${schema.description ? `<p class="mb-1"><small>${schema.description}</small></p>` : ''}
                    <details>
                        <summary>Ver Schema</summary>
                        <pre class="bg-light p-2 rounded mt-2">${schema.schema_content}</pre>
                    </details>
                </div>
            </div>
        `;
    });
    container.innerHTML = html;
}

async function createSchema() {
    const name = document.getElementById('schemaName').value.trim();
    const ownerId = document.getElementById('schemaOwner').value;
    const schemaType = document.getElementById('schemaType').value;
    const schemaContent = document.getElementById('schemaContent').value.trim();
    const description = document.getElementById('schemaDescription').value.trim();
    
    if (!name || !ownerId || !schemaType || !schemaContent) {
        showAlert('Campos obrigatórios não preenchidos', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/kafka/schemas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, owner_id: ownerId, schema_type: schemaType, schema_content: schemaContent, description })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('createSchemaModal')).hide();
            document.getElementById('schemaName').value = '';
            document.getElementById('schemaContent').value = '';
            document.getElementById('schemaDescription').value = '';
            loadSchemas();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

async function deleteSchema(schemaId, schemaName) {
    if (!confirm(`Deletar schema "${schemaName}"?`)) return;
    
    try {
        const response = await fetch(`/kafka/schemas/${schemaId}`, { method: 'DELETE' });
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            loadSchemas();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

// ==================== CLUSTERS ====================

async function loadClusters() {
    try {
        const response = await fetch('/kafka/clusters');
        const result = await response.json();
        
        if (result.success) {
            allClusters = result.clusters;
            filterClusters();
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

function filterClusters() {
    const ownerFilter = document.getElementById('filterOwner').value;
    const filtered = ownerFilter ? allClusters.filter(c => c.owner_id == ownerFilter) : allClusters;
    displayClusters(filtered);
}

function displayClusters(clusters) {
    const container = document.getElementById('clustersContainer');
    
    if (clusters.length === 0) {
        container.innerHTML = '<div class="text-center text-muted"><p>Nenhum cluster cadastrado</p></div>';
        return;
    }
    
    let html = '';
    clusters.forEach(cluster => {
        html += `
            <div class="card mb-3">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">${cluster.name}</h5>
                    <div>
                        <button class="btn btn-sm btn-success" onclick="viewTopics(${cluster.id}, '${cluster.name}')">
                            <i class="bi bi-list"></i> Tópicos
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteCluster(${cluster.id}, '${cluster.name}')">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <p class="mb-1"><strong>Dono:</strong> ${cluster.owner_name}</p>
                    <p class="mb-1"><strong>Bootstrap:</strong> <code>${cluster.bootstrap_servers}</code></p>
                    ${cluster.auth_name ? `<p class="mb-1"><strong>Auth:</strong> ${cluster.auth_name}</p>` : ''}
                    ${cluster.description ? `<p class="mb-0"><small>${cluster.description}</small></p>` : ''}
                </div>
            </div>
        `;
    });
    container.innerHTML = html;
}

async function createCluster() {
    const name = document.getElementById('clusterName').value.trim();
    const ownerId = document.getElementById('clusterOwner').value;
    const bootstrap = document.getElementById('clusterBootstrap').value.trim();
    const authId = document.getElementById('clusterAuth').value || null;
    const description = document.getElementById('clusterDescription').value.trim();
    
    if (!name || !ownerId || !bootstrap) {
        showAlert('Campos obrigatórios não preenchidos', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/kafka/clusters', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, owner_id: ownerId, bootstrap_servers: bootstrap, auth_id: authId, description })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('createClusterModal')).hide();
            document.getElementById('clusterName').value = '';
            document.getElementById('clusterBootstrap').value = '';
            document.getElementById('clusterDescription').value = '';
            loadClusters();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

async function deleteCluster(clusterId, clusterName) {
    if (!confirm(`Deletar cluster "${clusterName}"?`)) return;
    
    try {
        const response = await fetch(`/kafka/clusters/${clusterId}`, { method: 'DELETE' });
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            loadClusters();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

// ==================== TOPICS ====================

async function viewTopics(clusterId, clusterName) {
    currentClusterId = clusterId;
    document.getElementById('topicsModalTitle').textContent = `Tópicos - ${clusterName}`;
    
    try {
        const response = await fetch(`/kafka/topics/${clusterId}`);
        const result = await response.json();
        
        if (result.success) {
            displayTopics(result.topics);
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
    
    new bootstrap.Modal(document.getElementById('topicsModal')).show();
}

function displayTopics(topics) {
    const container = document.getElementById('topicsContainer');
    
    if (topics.length === 0) {
        container.innerHTML = '<div class="text-center text-muted"><p>Nenhum tópico cadastrado</p></div>';
        return;
    }
    
    let html = '<div class="list-group">';
    topics.forEach(topic => {
        html += `
            <div class="list-group-item">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-1">${topic.topic_name}</h6>
                        ${topic.schema_name ? `<small class="text-muted">Schema: ${topic.schema_name} (${topic.schema_type})</small>` : ''}
                    </div>
                    <div>
                        <button class="btn btn-sm btn-primary" onclick="openPublishModal(${topic.id}, '${topic.topic_name}')">
                            <i class="bi bi-send"></i> Publicar
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteTopic(${topic.id}, '${topic.topic_name}')">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}

async function deleteTopic(topicId, topicName) {
    if (!confirm(`Deletar tópico "${topicName}"?`)) return;
    
    try {
        const response = await fetch(`/kafka/topics/${topicId}`, { method: 'DELETE' });
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            viewTopics(currentClusterId, '');
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

// ==================== PUBLISH ====================

async function openPublishModal(topicId, topicName) {
    currentTopicId = topicId;
    
    // Carrega últimos parâmetros
    try {
        const response = await fetch(`/kafka/topics/${currentClusterId}`);
        const result = await response.json();
        
        if (result.success) {
            const topic = result.topics.find(t => t.id === topicId);
            if (topic) {
                if (topic.last_message_payload) {
                    document.getElementById('messagePayload').value = topic.last_message_payload;
                }
                if (topic.last_message_headers) {
                    document.getElementById('messageHeaders').value = topic.last_message_headers;
                }
            }
        }
    } catch (error) {
        console.error('Erro ao carregar parâmetros:', error);
    }
    
    document.getElementById('publishBtn').onclick = () => publishMessage(topicId);
    document.getElementById('clearPublishBtn').onclick = clearPublishFields;
    
    new bootstrap.Modal(document.getElementById('publishModal')).show();
}

async function publishMessage(topicId) {
    const key = document.getElementById('messageKey').value.trim() || null;
    const payloadText = document.getElementById('messagePayload').value.trim();
    const headersText = document.getElementById('messageHeaders').value.trim();
    
    if (!payloadText) {
        showAlert('Payload é obrigatório', 'warning');
        return;
    }
    
    let payload, headers = null;
    
    try {
        payload = JSON.parse(payloadText);
        if (headersText) headers = JSON.parse(headersText);
    } catch (e) {
        showAlert('JSON inválido', 'danger');
        return;
    }
    
    document.getElementById('publishResult').innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-success"></div>
            <p class="mt-2">Publicando...</p>
        </div>
    `;
    
    try {
        const response = await fetch(`/kafka/publish/${topicId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ payload, key, headers })
        });
        
        const result = await response.json();
        
        if (result.success) {
            document.getElementById('publishResult').innerHTML = `
                <div class="alert alert-success">
                    <strong>✅ Mensagem publicada!</strong><br>
                    Tópico: ${result.topic}<br>
                    Partição: ${result.partition}<br>
                    Offset: ${result.offset}
                </div>
            `;
            showAlert('Mensagem publicada com sucesso', 'success');
        } else {
            document.getElementById('publishResult').innerHTML = `
                <div class="alert alert-danger">${result.message}</div>
            `;
        }
    } catch (error) {
        document.getElementById('publishResult').innerHTML = `
            <div class="alert alert-danger">Erro: ${error.message}</div>
        `;
    }
}

function clearPublishFields() {
    document.getElementById('messageKey').value = '';
    document.getElementById('messagePayload').value = '';
    document.getElementById('messageHeaders').value = '';
    document.getElementById('publishResult').innerHTML = '<p class="text-muted">Publique uma mensagem para ver o resultado</p>';
}
