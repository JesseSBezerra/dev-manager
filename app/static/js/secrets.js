// JavaScript para Secrets Manager

const alertContainer = document.getElementById('alertContainer');
const secretsContainer = document.getElementById('secretsContainer');
const favoritesContainer = document.getElementById('favoritesContainer');
const refreshSecretsBtn = document.getElementById('refreshSecretsBtn');
const refreshFavoritesBtn = document.getElementById('refreshFavoritesBtn');
const createSecretBtn = document.getElementById('createSecretBtn');
const updateSecretBtn = document.getElementById('updateSecretBtn');
const copySecretBtn = document.getElementById('copySecretBtn');
const secretsFilter = document.getElementById('secretsFilter');
const clearFilterBtn = document.getElementById('clearFilterBtn');
const favoritesFilter = document.getElementById('favoritesFilter');
const clearFavoritesFilterBtn = document.getElementById('clearFavoritesFilterBtn');

let currentSecretForUpdate = null;
let currentSecretValue = null;
let allSecrets = [];
let allFavorites = [];

// Event Listeners
refreshSecretsBtn.addEventListener('click', loadSecrets);
refreshFavoritesBtn.addEventListener('click', loadFavorites);
createSecretBtn.addEventListener('click', createSecret);
updateSecretBtn.addEventListener('click', updateSecret);
if (copySecretBtn) {
    copySecretBtn.addEventListener('click', copySecretValue);
}
secretsFilter.addEventListener('input', filterSecrets);
clearFilterBtn.addEventListener('click', () => {
    secretsFilter.value = '';
    filterSecrets();
});
favoritesFilter.addEventListener('input', filterFavorites);
clearFavoritesFilterBtn.addEventListener('click', () => {
    favoritesFilter.value = '';
    filterFavorites();
});

// Alternar entre texto simples e JSON
document.getElementById('secretValueType').addEventListener('change', (e) => {
    const plaintextContainer = document.getElementById('plaintextContainer');
    const jsonContainer = document.getElementById('jsonContainer');
    
    if (e.target.value === 'json') {
        plaintextContainer.style.display = 'none';
        jsonContainer.style.display = 'block';
    } else {
        plaintextContainer.style.display = 'block';
        jsonContainer.style.display = 'none';
    }
});

// Carregar ao iniciar
document.addEventListener('DOMContentLoaded', () => {
    loadSecrets();
    loadFavorites();
});

// Atualizar favoritos quando trocar para aba Favoritos
document.getElementById('favorites-tab').addEventListener('shown.bs.tab', loadFavorites);

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
    
    alertContainer.innerHTML = '';
    alertContainer.appendChild(alertDiv);
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    setTimeout(() => {
        alertDiv.remove();
    }, 8000);
}

/**
 * Carrega lista de segredos
 */
async function loadSecrets() {
    secretsContainer.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2">Carregando segredos...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/secrets/list');
        const result = await response.json();
        
        if (result.success) {
            allSecrets = result.secrets;
            displaySecrets(allSecrets);
        } else {
            secretsContainer.innerHTML = `
                <div class="alert alert-danger">
                    ${result.message}
                </div>
            `;
        }
    } catch (error) {
        secretsContainer.innerHTML = `
            <div class="alert alert-danger">
                Erro ao carregar segredos: ${error.message}
            </div>
        `;
    }
}

/**
 * Exibe lista de segredos
 */
function displaySecrets(secrets) {
    if (secrets.length === 0) {
        secretsContainer.innerHTML = `
            <div class="text-center text-muted">
                <i class="bi bi-inbox" style="font-size: 3rem;"></i>
                <p class="mt-2">Nenhum segredo encontrado</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="table-responsive"><table class="table table-hover">';
    html += `
        <thead class="table-dark">
            <tr>
                <th>Nome</th>
                <th>Descrição</th>
                <th>Última Modificação</th>
                <th>Rotação</th>
                <th>Ações</th>
            </tr>
        </thead>
        <tbody>
    `;
    
    secrets.forEach(secret => {
        const isDeleted = secret.deleted_date !== null;
        const rowClass = isDeleted ? 'table-danger' : '';
        
        html += `
            <tr class="${rowClass}">
                <td>
                    <i class="bi bi-key text-primary"></i>
                    <strong>${secret.name}</strong>
                    ${isDeleted ? '<span class="badge bg-danger ms-2">Deletado</span>' : ''}
                </td>
                <td>${secret.description}</td>
                <td>${formatDate(secret.last_changed_date)}</td>
                <td>
                    ${secret.rotation_enabled ? 
                        '<span class="badge bg-success">Ativa</span>' : 
                        '<span class="badge bg-secondary">Inativa</span>'}
                </td>
                <td>
                    ${!isDeleted ? `
                        <button class="btn btn-sm btn-warning" onclick="toggleFavorite('${secret.name}')" title="Adicionar aos favoritos">
                            <i class="bi bi-star"></i>
                        </button>
                        <button class="btn btn-sm btn-success" onclick="viewSecretValue('${secret.name}')" title="Ver Valor">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-info" onclick="viewSecretDetails('${secret.name}')" title="Detalhes">
                            <i class="bi bi-info-circle"></i>
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="openUpdateModal('${secret.name}')" title="Atualizar">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteSecret('${secret.name}')" title="Deletar">
                            <i class="bi bi-trash"></i>
                        </button>
                    ` : `
                        <button class="btn btn-sm btn-primary" onclick="restoreSecret('${secret.name}')" title="Restaurar">
                            <i class="bi bi-arrow-counterclockwise"></i> Restaurar
                        </button>
                    `}
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table></div>';
    secretsContainer.innerHTML = html;
}

/**
 * Cria um novo segredo
 */
async function createSecret() {
    const name = document.getElementById('secretName').value.trim();
    const description = document.getElementById('secretDescription').value.trim();
    const valueType = document.getElementById('secretValueType').value;
    
    let secretValue;
    
    if (valueType === 'json') {
        // Constrói JSON a partir dos pares chave/valor
        const pairs = {};
        const keys = document.querySelectorAll('.json-key');
        const values = document.querySelectorAll('.json-value');
        
        for (let i = 0; i < keys.length; i++) {
            const key = keys[i].value.trim();
            const value = values[i].value.trim();
            if (key) {
                pairs[key] = value;
            }
        }
        
        secretValue = JSON.stringify(pairs, null, 2);
    } else {
        secretValue = document.getElementById('secretValuePlaintext').value;
    }
    
    if (!name || !secretValue) {
        showAlert('Preencha o nome e o valor do segredo', 'warning');
        return;
    }
    
    createSecretBtn.disabled = true;
    createSecretBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Criando...';
    
    try {
        const response = await fetch('/secrets/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                secret_value: secretValue,
                description: description || null
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('createSecretModal')).hide();
            document.getElementById('createSecretForm').reset();
            loadSecrets();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro ao criar segredo: ${error.message}`, 'danger');
    } finally {
        createSecretBtn.disabled = false;
        createSecretBtn.innerHTML = '<i class="bi bi-save"></i> Criar Segredo';
    }
}

/**
 * Visualiza o valor de um segredo
 */
async function viewSecretValue(secretName) {
    const modal = new bootstrap.Modal(document.getElementById('viewSecretModal'));
    const valueContainer = document.getElementById('viewSecretValue');
    
    document.getElementById('viewSecretName').textContent = secretName;
    valueContainer.innerHTML = '<div class="spinner-border text-success"></div>';
    
    modal.show();
    
    try {
        const response = await fetch(`/secrets/${encodeURIComponent(secretName)}/value`);
        const result = await response.json();
        
        if (result.success) {
            currentSecretValue = result.secret_string;
            
            if (result.is_json && result.secret_json) {
                // Exibe JSON formatado
                let html = '<div class="table-responsive"><table class="table table-sm table-bordered">';
                html += '<thead><tr><th>Chave</th><th>Valor</th></tr></thead><tbody>';
                
                for (const [key, value] of Object.entries(result.secret_json)) {
                    html += `<tr><td><strong>${key}</strong></td><td class="font-monospace">${value}</td></tr>`;
                }
                
                html += '</tbody></table></div>';
                html += '<hr><p class="text-muted"><strong>JSON Completo:</strong></p>';
                html += `<pre class="bg-light p-3 rounded"><code>${JSON.stringify(result.secret_json, null, 2)}</code></pre>`;
                
                valueContainer.innerHTML = html;
            } else {
                // Exibe texto simples
                valueContainer.innerHTML = `<pre class="bg-light p-3 rounded"><code>${result.secret_string}</code></pre>`;
            }
        } else {
            valueContainer.innerHTML = `<div class="alert alert-danger">${result.message}</div>`;
        }
    } catch (error) {
        valueContainer.innerHTML = `<div class="alert alert-danger">Erro: ${error.message}</div>`;
    }
}

/**
 * Copia o valor do segredo
 */
function copySecretValue() {
    if (currentSecretValue) {
        navigator.clipboard.writeText(currentSecretValue).then(() => {
            showAlert('Valor copiado para a área de transferência', 'success');
        }).catch(err => {
            showAlert('Erro ao copiar: ' + err, 'danger');
        });
    }
}

/**
 * Abre modal para atualizar segredo
 */
function openUpdateModal(secretName) {
    currentSecretForUpdate = secretName;
    document.getElementById('updateSecretName').textContent = secretName;
    document.getElementById('updateSecretValue').value = '';
    
    const modal = new bootstrap.Modal(document.getElementById('updateSecretModal'));
    modal.show();
}

/**
 * Atualiza um segredo
 */
async function updateSecret() {
    const newValue = document.getElementById('updateSecretValue').value;
    
    if (!newValue) {
        showAlert('Digite o novo valor', 'warning');
        return;
    }
    
    updateSecretBtn.disabled = true;
    updateSecretBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Atualizando...';
    
    try {
        const response = await fetch(`/secrets/${encodeURIComponent(currentSecretForUpdate)}/update`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                secret_value: newValue
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('updateSecretModal')).hide();
            loadSecrets();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro ao atualizar: ${error.message}`, 'danger');
    } finally {
        updateSecretBtn.disabled = false;
        updateSecretBtn.innerHTML = '<i class="bi bi-save"></i> Atualizar';
    }
}

/**
 * Deleta um segredo
 */
async function deleteSecret(secretName) {
    if (!confirm(`Tem certeza que deseja deletar o segredo "${secretName}"?\n\nEle será agendado para deleção em 30 dias e poderá ser restaurado neste período.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/secrets/${encodeURIComponent(secretName)}/delete`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            loadSecrets();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro ao deletar: ${error.message}`, 'danger');
    }
}

/**
 * Restaura um segredo deletado
 */
async function restoreSecret(secretName) {
    if (!confirm(`Restaurar o segredo "${secretName}"?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/secrets/${encodeURIComponent(secretName)}/restore`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            loadSecrets();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro ao restaurar: ${error.message}`, 'danger');
    }
}

/**
 * Visualiza detalhes do segredo
 */
async function viewSecretDetails(secretName) {
    const modal = new bootstrap.Modal(document.getElementById('detailsModal'));
    const modalBody = document.getElementById('detailsModalBody');
    
    modalBody.innerHTML = '<div class="text-center"><div class="spinner-border text-info"></div></div>';
    modal.show();
    
    try {
        const response = await fetch(`/secrets/${encodeURIComponent(secretName)}`);
        const result = await response.json();
        
        if (result.success) {
            const secret = result.secret;
            
            let html = `
                <table class="table table-bordered">
                    <tr><th>Nome</th><td class="font-monospace">${secret.name}</td></tr>
                    <tr><th>ARN</th><td class="font-monospace small">${secret.arn}</td></tr>
                    <tr><th>Descrição</th><td>${secret.description}</td></tr>
                    <tr><th>Criado em</th><td>${formatDate(secret.created_date)}</td></tr>
                    <tr><th>Última modificação</th><td>${formatDate(secret.last_changed_date)}</td></tr>
                    <tr><th>Último acesso</th><td>${formatDate(secret.last_accessed_date)}</td></tr>
                    <tr><th>Rotação</th><td>${secret.rotation_enabled ? 
                        '<span class="badge bg-success">Ativa</span>' : 
                        '<span class="badge bg-secondary">Inativa</span>'}</td></tr>
                </table>
            `;
            
            if (secret.tags && secret.tags.length > 0) {
                html += '<h6>Tags:</h6><div class="mb-2">';
                secret.tags.forEach(tag => {
                    html += `<span class="badge bg-info me-1">${tag.Key}: ${tag.Value}</span>`;
                });
                html += '</div>';
            }
            
            modalBody.innerHTML = html;
        } else {
            modalBody.innerHTML = `<div class="alert alert-danger">${result.message}</div>`;
        }
    } catch (error) {
        modalBody.innerHTML = `<div class="alert alert-danger">Erro: ${error.message}</div>`;
    }
}

/**
 * Adiciona um par chave/valor JSON
 */
function addJsonPair() {
    const container = document.getElementById('jsonPairs');
    const newPair = document.createElement('div');
    newPair.className = 'row mb-2';
    newPair.innerHTML = `
        <div class="col-md-5">
            <input type="text" class="form-control json-key" placeholder="Chave">
        </div>
        <div class="col-md-6">
            <input type="text" class="form-control json-value" placeholder="Valor">
        </div>
        <div class="col-md-1">
            <button type="button" class="btn btn-sm btn-danger" onclick="removeJsonPair(this)">
                <i class="bi bi-trash"></i>
            </button>
        </div>
    `;
    container.appendChild(newPair);
}

/**
 * Remove um par chave/valor JSON
 */
function removeJsonPair(button) {
    button.closest('.row').remove();
}

/**
 * Formata data
 */
function formatDate(dateString) {
    if (!dateString || dateString === 'N/A' || dateString === 'Nunca') {
        return dateString;
    }
    
    try {
        const date = new Date(dateString);
        return date.toLocaleString('pt-BR');
    } catch {
        return dateString;
    }
}

// ==================== FILTROS ====================

/**
 * Filtra segredos
 */
function filterSecrets() {
    const filter = secretsFilter.value.toLowerCase();
    
    if (!filter) {
        displaySecrets(allSecrets);
        return;
    }
    
    const filtered = allSecrets.filter(secret => 
        secret.name.toLowerCase().includes(filter) ||
        (secret.description && secret.description.toLowerCase().includes(filter))
    );
    
    displaySecrets(filtered);
}

/**
 * Filtra favoritos
 */
function filterFavorites() {
    const filter = favoritesFilter.value.toLowerCase();
    
    if (!filter) {
        displayFavorites(allFavorites);
        return;
    }
    
    const filtered = allFavorites.filter(fav => 
        fav.secret_name.toLowerCase().includes(filter) ||
        (fav.alias && fav.alias.toLowerCase().includes(filter))
    );
    
    displayFavorites(filtered);
}

// ==================== FAVORITOS ====================

/**
 * Carrega favoritos
 */
async function loadFavorites() {
    favoritesContainer.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-warning" role="status"></div>
            <p class="mt-2">Carregando favoritos...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/secrets/favorites');
        const result = await response.json();
        
        if (result.success) {
            allFavorites = result.favorites;
            displayFavorites(allFavorites);
        } else {
            favoritesContainer.innerHTML = `
                <div class="alert alert-danger">
                    ${result.message}
                </div>
            `;
        }
    } catch (error) {
        favoritesContainer.innerHTML = `
            <div class="alert alert-danger">
                Erro ao carregar favoritos: ${error.message}
            </div>
        `;
    }
}

/**
 * Exibe lista de favoritos
 */
function displayFavorites(favorites) {
    if (favorites.length === 0) {
        favoritesContainer.innerHTML = `
            <div class="text-center text-muted">
                <i class="bi bi-star" style="font-size: 3rem;"></i>
                <p class="mt-2">Nenhum secret favoritado ainda</p>
                <p class="small">Clique na estrela ⭐ em qualquer secret para adicionar aos favoritos</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="table-responsive"><table class="table table-hover">';
    html += `
        <thead class="table-dark">
            <tr>
                <th>Nome</th>
                <th>Favoritado em</th>
                <th>Ações</th>
            </tr>
        </thead>
        <tbody>
    `;
    
    favorites.forEach(fav => {
        html += `
            <tr>
                <td>
                    <i class="bi bi-star-fill text-warning"></i>
                    <strong>${fav.secret_name}</strong>
                    ${fav.alias ? `<span class="badge bg-secondary ms-2">${fav.alias}</span>` : ''}
                </td>
                <td>${formatDate(fav.created_at)}</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="removeFavorite('${fav.secret_name}')" title="Remover dos favoritos">
                        <i class="bi bi-star-fill"></i>
                    </button>
                    <button class="btn btn-sm btn-success" onclick="viewSecretValue('${fav.secret_name}')" title="Ver Valor">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-info" onclick="viewSecretDetails('${fav.secret_name}')" title="Detalhes">
                        <i class="bi bi-info-circle"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table></div>';
    favoritesContainer.innerHTML = html;
}

/**
 * Adiciona/Remove favorito (toggle sem confirmação)
 */
async function toggleFavorite(secretName) {
    try {
        // Encode completo para usar na URL
        const encoded = encodeURIComponent(secretName);
        
        // Verifica se já é favorito
        const checkResponse = await fetch(`/secrets/favorites/check/${encoded}`);
        const checkResult = await checkResponse.json();
        
        if (checkResult.is_favorite) {
            // Remove sem confirmação
            const response = await fetch(`/secrets/favorites/${encoded}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.success) {
                showAlert(result.message, 'success');
                loadFavorites();
                loadSecrets(); // Atualiza a lista principal
            } else {
                showAlert(result.message, 'danger');
            }
        } else {
            // Adiciona
            const response = await fetch('/secrets/favorites', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    secret_name: secretName
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                showAlert(result.message, 'success');
                loadFavorites();
                loadSecrets(); // Atualiza a lista principal
            } else {
                showAlert(result.message, 'danger');
            }
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

/**
 * Remove favorito (com confirmação - usado no botão da aba favoritos)
 */
async function removeFavorite(secretName) {
    if (!confirm(`Remover "${secretName}" dos favoritos?`)) {
        return;
    }
    
    try {
        // Encode completo para preservar caracteres especiais
        const encoded = encodeURIComponent(secretName);
        const response = await fetch(`/secrets/favorites/${encoded}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            loadFavorites();
            loadSecrets(); // Atualiza a lista principal também
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}
