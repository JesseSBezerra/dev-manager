// JavaScript para API Catalog

const alertContainer = document.getElementById('alertContainer');
const apisContainer = document.getElementById('apisContainer');
const ownersContainer = document.getElementById('ownersContainer');
const authContainer = document.getElementById('authContainer');

let currentApiId = null;
let currentRequestId = null;
let allOwners = [];
let allApis = [];
let allAuths = [];

// Event Listeners
document.getElementById('refreshApisBtn').addEventListener('click', loadApis);
document.getElementById('refreshOwnersBtn').addEventListener('click', loadOwners);
document.getElementById('refreshAuthBtn').addEventListener('click', loadAuthentications);
document.getElementById('createOwnerBtn').addEventListener('click', createOwner);
document.getElementById('createApiBtn').addEventListener('click', createApi);
document.getElementById('createAuthBtn').addEventListener('click', createAuthentication);
document.getElementById('filterOwner').addEventListener('change', filterApis);
document.getElementById('filterAuthOwner').addEventListener('change', filterAuthentications);
document.getElementById('executeTestBtn').addEventListener('click', executeTest);
document.getElementById('clearTestBtn').addEventListener('click', clearTestFields);

// Carregar ao iniciar
document.addEventListener('DOMContentLoaded', () => {
    loadOwners();
    loadApis();
    loadAuthentications();
});

// Atualizar selects quando trocar de aba
document.getElementById('apis-tab').addEventListener('shown.bs.tab', () => {
    populateOwnerSelects();
});

document.getElementById('auth-tab').addEventListener('shown.bs.tab', () => {
    populateOwnerSelects();
});

/**
 * Exibe um alerta
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

// ==================== OWNERS ====================

async function loadOwners() {
    const container = ownersContainer;
    container.innerHTML = '<div class="text-center"><div class="spinner-border"></div></div>';
    
    try {
        const response = await fetch('/api-catalog/owners');
        const result = await response.json();
        
        if (result.success) {
            allOwners = result.owners;
            displayOwners(allOwners);
            populateOwnerSelects();
        } else {
            container.innerHTML = `<div class="alert alert-danger">${result.message}</div>`;
        }
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">Erro: ${error.message}</div>`;
    }
}

function displayOwners(owners) {
    const container = ownersContainer;
    
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
        const response = await fetch('/api-catalog/owners', {
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
    if (!confirm(`Deletar dono "${ownerName}"? Isso deletará todas as APIs associadas.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api-catalog/owners/${ownerId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            loadOwners();
            loadApis();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

function populateOwnerSelects() {
    const selects = [
        document.getElementById('apiOwner'),
        document.getElementById('authOwner'),
        document.getElementById('filterOwner'),
        document.getElementById('filterAuthOwner')
    ];
    
    selects.forEach(select => {
        if (!select) return;
        
        const currentValue = select.value;
        const isFilter = select.id.startsWith('filter');
        
        select.innerHTML = isFilter ? '<option value="">Todos os donos</option>' : '<option value="">Selecione...</option>';
        
        allOwners.forEach(owner => {
            const option = document.createElement('option');
            option.value = owner.id;
            option.textContent = owner.name;
            select.appendChild(option);
        });
        
        if (currentValue) {
            select.value = currentValue;
        }
    });
}

// ==================== APIS ====================

async function loadApis() {
    const container = apisContainer;
    container.innerHTML = '<div class="text-center"><div class="spinner-border"></div></div>';
    
    try {
        const response = await fetch('/api-catalog/apis');
        const result = await response.json();
        
        if (result.success) {
            allApis = result.apis;
            filterApis();
        } else {
            container.innerHTML = `<div class="alert alert-danger">${result.message}</div>`;
        }
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">Erro: ${error.message}</div>`;
    }
}

function filterApis() {
    const ownerFilter = document.getElementById('filterOwner').value;
    const filtered = ownerFilter ? allApis.filter(api => api.owner_id == ownerFilter) : allApis;
    displayApis(filtered);
}

function displayApis(apis) {
    const container = apisContainer;
    
    if (apis.length === 0) {
        container.innerHTML = '<div class="text-center text-muted"><p>Nenhuma API encontrada</p></div>';
        return;
    }
    
    let html = '';
    apis.forEach(api => {
        html += `
            <div class="card mb-3">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">${api.name}</h5>
                    <div>
                        <button class="btn btn-sm btn-primary" onclick="viewApiDetails('${api.id}')">
                            <i class="bi bi-eye"></i> Ver
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteApi('${api.id}', '${api.name}')">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <p class="mb-1"><strong>Dono:</strong> ${api.owner_name}</p>
                    ${api.base_url ? `<p class="mb-1"><strong>Base URL:</strong> <code>${api.base_url}</code></p>` : ''}
                    ${api.description ? `<p class="mb-0"><small class="text-muted">${api.description}</small></p>` : ''}
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

async function createApi() {
    const name = document.getElementById('apiName').value.trim();
    const ownerId = document.getElementById('apiOwner').value;
    const baseUrl = document.getElementById('apiBaseUrl').value.trim();
    const description = document.getElementById('apiDescription').value.trim();
    
    if (!name || !ownerId) {
        showAlert('Nome e Dono são obrigatórios', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api-catalog/apis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, owner_id: ownerId, base_url: baseUrl, description })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('createApiModal')).hide();
            document.getElementById('apiName').value = '';
            document.getElementById('apiBaseUrl').value = '';
            document.getElementById('apiDescription').value = '';
            loadApis();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

async function deleteApi(apiId, apiName) {
    if (!confirm(`Deletar API "${apiName}"?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api-catalog/apis/${apiId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            loadApis();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

function viewApiDetails(apiId) {
    currentApiId = apiId;
    window.location.href = `/api-catalog/api/${apiId}`;
}

// ==================== AUTHENTICATIONS ====================

async function loadAuthentications() {
    const container = authContainer;
    container.innerHTML = '<div class="text-center"><div class="spinner-border"></div></div>';
    
    try {
        const response = await fetch('/api-catalog/authentications');
        const result = await response.json();
        
        if (result.success) {
            allAuths = result.authentications;
            filterAuthentications();
        } else {
            container.innerHTML = `<div class="alert alert-danger">${result.message}</div>`;
        }
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">Erro: ${error.message}</div>`;
    }
}

function filterAuthentications() {
    const ownerFilter = document.getElementById('filterAuthOwner').value;
    const filtered = ownerFilter ? allAuths.filter(auth => auth.owner_id == ownerFilter) : allAuths;
    displayAuthentications(filtered);
}

function displayAuthentications(auths) {
    const container = authContainer;
    
    if (auths.length === 0) {
        container.innerHTML = '<div class="text-center text-muted"><p>Nenhuma autenticação encontrada</p></div>';
        return;
    }
    
    let html = '<div class="list-group">';
    auths.forEach(auth => {
        const typeBadge = {
            'bearer': 'primary',
            'basic': 'info',
            'apikey': 'warning',
            'oauth2': 'success'
        }[auth.auth_type] || 'secondary';
        
        html += `
            <div class="list-group-item">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-1">
                            ${auth.name}
                            <span class="badge bg-${typeBadge}">${auth.auth_type}</span>
                        </h6>
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
    const authConfig = document.getElementById('authConfig').value.trim();
    const tokenField = document.getElementById('authTokenField').value.trim();
    
    if (!name || !ownerId || !authType) {
        showAlert('Nome, Dono e Tipo são obrigatórios', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api-catalog/authentications', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, owner_id: ownerId, auth_type: authType, auth_config: authConfig, token_field: tokenField })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('createAuthModal')).hide();
            document.getElementById('authName').value = '';
            document.getElementById('authConfig').value = '';
            document.getElementById('authTokenField').value = '';
            loadAuthentications();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

async function deleteAuth(authId, authName) {
    if (!confirm(`Deletar autenticação "${authName}"?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api-catalog/authentications/${authId}`, {
            method: 'DELETE'
        });
        
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

// ==================== TEST ====================

async function openTestModal(requestId) {
    currentRequestId = requestId;
    
    // Limpa campos
    document.getElementById('testRequestBody').value = '';
    document.getElementById('testRequestQuery').value = '';
    document.getElementById('testRequestHeaders').value = '';
    document.getElementById('testResponseContainer').innerHTML = '<p class="text-muted">Execute a request para ver a resposta</p>';
    
    // Carrega parâmetros salvos
    try {
        const response = await fetch(`/api-catalog/test-params/${requestId}`);
        const result = await response.json();
        
        if (result.success) {
            if (result.body) document.getElementById('testRequestBody').value = result.body;
            if (result.query_params) document.getElementById('testRequestQuery').value = result.query_params;
            if (result.headers) document.getElementById('testRequestHeaders').value = result.headers;
        }
    } catch (error) {
        console.error('Erro ao carregar parâmetros:', error);
    }
    
    new bootstrap.Modal(document.getElementById('testRequestModal')).show();
}

async function executeTest() {
    const bodyText = document.getElementById('testRequestBody').value.trim();
    const queryText = document.getElementById('testRequestQuery').value.trim();
    const headersText = document.getElementById('testRequestHeaders').value.trim();
    
    let body = null;
    let query_params = null;
    let headers = null;
    
    try {
        if (bodyText) body = JSON.parse(bodyText);
        if (queryText) query_params = JSON.parse(queryText);
        if (headersText) headers = JSON.parse(headersText);
    } catch (e) {
        showAlert('JSON inválido', 'danger');
        return;
    }
    
    document.getElementById('testResponseContainer').innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-success" role="status"></div>
            <p class="mt-2">Executando...</p>
        </div>
    `;
    
    try {
        const response = await fetch(`/api-catalog/test/${currentRequestId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ body, query_params, headers })
        });
        
        const result = await response.json();
        
        if (result.success) {
            const resp = result.response;
            const statusColor = resp.status_code < 300 ? 'success' : resp.status_code < 400 ? 'warning' : 'danger';
            
            let html = `
                <div class="alert alert-${statusColor}">
                    <strong>Status:</strong> ${resp.status_code}
                </div>
                <div class="mb-3">
                    <strong>Headers:</strong>
                    <pre class="bg-light p-2 rounded">${JSON.stringify(resp.headers, null, 2)}</pre>
                </div>
                <div class="mb-3">
                    <strong>Body:</strong>
                    <pre class="bg-light p-2 rounded" style="max-height: 400px; overflow-y: auto;">${resp.json ? JSON.stringify(resp.json, null, 2) : resp.body}</pre>
                </div>
            `;
            
            document.getElementById('testResponseContainer').innerHTML = html;
            showAlert('Parâmetros salvos automaticamente', 'success');
        } else {
            document.getElementById('testResponseContainer').innerHTML = `
                <div class="alert alert-danger">${result.message}</div>
            `;
        }
    } catch (error) {
        document.getElementById('testResponseContainer').innerHTML = `
            <div class="alert alert-danger">Erro: ${error.message}</div>
        `;
    }
}

function clearTestFields() {
    document.getElementById('testRequestBody').value = '';
    document.getElementById('testRequestQuery').value = '';
    document.getElementById('testRequestHeaders').value = '';
    document.getElementById('testResponseContainer').innerHTML = '<p class="text-muted">Execute a request para ver a resposta</p>';
}
