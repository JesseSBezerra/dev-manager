// JavaScript para Parameter Store

const alertContainer = document.getElementById('alertContainer');
const parametersContainer = document.getElementById('parametersContainer');
const favoritesContainer = document.getElementById('favoritesContainer');
const refreshParametersBtn = document.getElementById('refreshParametersBtn');
const refreshFavoritesBtn = document.getElementById('refreshFavoritesBtn');
const createParameterBtn = document.getElementById('createParameterBtn');
const updateParameterBtn = document.getElementById('updateParameterBtn');
const copyValueBtn = document.getElementById('copyValueBtn');
const parametersFilter = document.getElementById('parametersFilter');
const clearFilterBtn = document.getElementById('clearFilterBtn');
const favoritesFilter = document.getElementById('favoritesFilter');
const clearFavoritesFilterBtn = document.getElementById('clearFavoritesFilterBtn');

let allParameters = [];
let allFavorites = [];
let currentParameterName = null;
let currentParameterValue = null;

// Event Listeners
refreshParametersBtn.addEventListener('click', loadParameters);
refreshFavoritesBtn.addEventListener('click', loadFavorites);
createParameterBtn.addEventListener('click', createParameter);
updateParameterBtn.addEventListener('click', updateParameter);
if (copyValueBtn) {
    copyValueBtn.addEventListener('click', copyValue);
}
parametersFilter.addEventListener('input', filterParameters);
clearFilterBtn.addEventListener('click', () => {
    parametersFilter.value = '';
    filterParameters();
});
favoritesFilter.addEventListener('input', filterFavorites);
clearFavoritesFilterBtn.addEventListener('click', () => {
    favoritesFilter.value = '';
    filterFavorites();
});

// Carregar ao iniciar
document.addEventListener('DOMContentLoaded', () => {
    loadParameters();
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
    
    alertContainer.appendChild(alertDiv);
    
    // Remove após 5 segundos
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

/**
 * Carrega lista de parâmetros
 */
async function loadParameters() {
    parametersContainer.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2">Carregando parâmetros...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/parameters/list');
        const result = await response.json();
        
        if (result.success) {
            allParameters = result.parameters;
            displayParameters(allParameters);
        } else {
            parametersContainer.innerHTML = `
                <div class="alert alert-danger">
                    ${result.message}
                </div>
            `;
        }
    } catch (error) {
        parametersContainer.innerHTML = `
            <div class="alert alert-danger">
                Erro ao carregar parâmetros: ${error.message}
            </div>
        `;
    }
}

/**
 * Exibe lista de parâmetros
 */
function displayParameters(parameters) {
    if (parameters.length === 0) {
        parametersContainer.innerHTML = `
            <div class="text-center text-muted">
                <i class="bi bi-inbox" style="font-size: 3rem;"></i>
                <p class="mt-2">Nenhum parâmetro encontrado</p>
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
                <th>Descrição</th>
                <th>Versão</th>
                <th>Ações</th>
            </tr>
        </thead>
        <tbody>
    `;
    
    parameters.forEach(param => {
        const typeColor = param.type === 'SecureString' ? 'danger' : param.type === 'StringList' ? 'info' : 'secondary';
        
        html += `
            <tr>
                <td>
                    <i class="bi bi-sliders text-primary"></i>
                    <strong class="font-monospace">${param.name}</strong>
                </td>
                <td><span class="badge bg-${typeColor}">${param.type}</span></td>
                <td>${param.description}</td>
                <td><span class="badge bg-secondary">v${param.version}</span></td>
                <td>
                    <button class="btn btn-sm btn-warning" onclick="toggleFavorite('${param.name}')" title="Adicionar aos favoritos">
                        <i class="bi bi-star"></i>
                    </button>
                    <button class="btn btn-sm btn-success" onclick="viewParameterValue('${param.name}')" title="Ver Valor">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-info" onclick="viewHistory('${param.name}')" title="Histórico">
                        <i class="bi bi-clock-history"></i>
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="openUpdateModal('${param.name}')" title="Atualizar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteParameter('${param.name}')" title="Deletar">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table></div>';
    parametersContainer.innerHTML = html;
}

/**
 * Filtra parâmetros
 */
function filterParameters() {
    const filter = parametersFilter.value.toLowerCase();
    
    if (!filter) {
        displayParameters(allParameters);
        return;
    }
    
    const filtered = allParameters.filter(param => 
        param.name.toLowerCase().includes(filter) ||
        (param.description && param.description.toLowerCase().includes(filter))
    );
    
    displayParameters(filtered);
}

/**
 * Cria novo parâmetro
 */
async function createParameter() {
    const name = document.getElementById('parameterName').value.trim();
    const type = document.getElementById('parameterType').value;
    const value = document.getElementById('parameterValue').value.trim();
    const description = document.getElementById('parameterDescription').value.trim();
    
    if (!name || !value) {
        showAlert('Nome e valor são obrigatórios', 'warning');
        return;
    }
    
    createParameterBtn.disabled = true;
    createParameterBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Criando...';
    
    try {
        const response = await fetch('/parameters/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                value: value,
                type: type,
                description: description
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('createParameterModal')).hide();
            document.getElementById('parameterName').value = '';
            document.getElementById('parameterValue').value = '';
            document.getElementById('parameterDescription').value = '';
            loadParameters();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    } finally {
        createParameterBtn.disabled = false;
        createParameterBtn.innerHTML = '<i class="bi bi-plus-circle"></i> Criar';
    }
}

/**
 * Visualiza valor do parâmetro
 */
async function viewParameterValue(parameterName) {
    try {
        const encoded = encodeURIComponent(parameterName);
        const response = await fetch(`/parameters/${encoded}/value`);
        const result = await response.json();
        
        if (result.success) {
            const param = result.parameter;
            currentParameterValue = param.Value;
            
            document.getElementById('viewParamName').textContent = param.Name;
            document.getElementById('viewParamValue').textContent = param.Value;
            document.getElementById('viewParamType').textContent = param.Type;
            document.getElementById('viewParamVersion').textContent = `v${param.Version}`;
            
            new bootstrap.Modal(document.getElementById('viewValueModal')).show();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

/**
 * Copia valor para clipboard
 */
function copyValue() {
    if (currentParameterValue) {
        navigator.clipboard.writeText(currentParameterValue);
        showAlert('Valor copiado para a área de transferência!', 'success');
    }
}

/**
 * Abre modal de atualização
 */
async function openUpdateModal(parameterName) {
    currentParameterName = parameterName;
    
    try {
        const encoded = encodeURIComponent(parameterName);
        const response = await fetch(`/parameters/${encoded}/value`);
        const result = await response.json();
        
        if (result.success) {
            const param = result.parameter;
            
            document.getElementById('updateParamName').textContent = param.Name;
            document.getElementById('updateParameterValue').value = param.Value;
            document.getElementById('updateParameterDescription').value = '';
            
            new bootstrap.Modal(document.getElementById('updateParameterModal')).show();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

/**
 * Atualiza parâmetro
 */
async function updateParameter() {
    const value = document.getElementById('updateParameterValue').value.trim();
    const description = document.getElementById('updateParameterDescription').value.trim();
    
    if (!value) {
        showAlert('Valor é obrigatório', 'warning');
        return;
    }
    
    updateParameterBtn.disabled = true;
    updateParameterBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Atualizando...';
    
    try {
        const encoded = encodeURIComponent(currentParameterName);
        const response = await fetch(`/parameters/${encoded}/update`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                value: value,
                description: description
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('updateParameterModal')).hide();
            loadParameters();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    } finally {
        updateParameterBtn.disabled = false;
        updateParameterBtn.innerHTML = '<i class="bi bi-pencil"></i> Atualizar';
    }
}

/**
 * Deleta parâmetro
 */
async function deleteParameter(parameterName) {
    if (!confirm(`Tem certeza que deseja deletar o parâmetro "${parameterName}"?`)) {
        return;
    }
    
    try {
        const encoded = encodeURIComponent(parameterName);
        const response = await fetch(`/parameters/${encoded}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            loadParameters();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

/**
 * Visualiza histórico
 */
async function viewHistory(parameterName) {
    const historyBody = document.getElementById('historyBody');
    historyBody.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-info" role="status"></div>
            <p class="mt-2">Carregando histórico...</p>
        </div>
    `;
    
    new bootstrap.Modal(document.getElementById('historyModal')).show();
    
    try {
        const encoded = encodeURIComponent(parameterName);
        const response = await fetch(`/parameters/${encoded}/history`);
        const result = await response.json();
        
        if (result.success && result.history.length > 0) {
            let html = '<div class="table-responsive"><table class="table table-striped">';
            html += `
                <thead>
                    <tr>
                        <th>Versão</th>
                        <th>Valor</th>
                        <th>Data</th>
                    </tr>
                </thead>
                <tbody>
            `;
            
            result.history.forEach(item => {
                html += `
                    <tr>
                        <td><span class="badge bg-secondary">v${item.Version}</span></td>
                        <td><pre class="mb-0">${item.Value}</pre></td>
                        <td>${new Date(item.LastModifiedDate).toLocaleString('pt-BR')}</td>
                    </tr>
                `;
            });
            
            html += '</tbody></table></div>';
            historyBody.innerHTML = html;
        } else {
            historyBody.innerHTML = '<p class="text-muted">Nenhum histórico disponível</p>';
        }
    } catch (error) {
        historyBody.innerHTML = `<div class="alert alert-danger">Erro: ${error.message}</div>`;
    }
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
        const response = await fetch('/parameters/favorites');
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
                <p class="mt-2">Nenhum parâmetro favoritado ainda</p>
                <p class="small">Clique na estrela ⭐ em qualquer parâmetro para adicionar aos favoritos</p>
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
                    <strong class="font-monospace">${fav.parameter_name}</strong>
                    ${fav.alias ? `<span class="badge bg-secondary ms-2">${fav.alias}</span>` : ''}
                </td>
                <td>${new Date(fav.created_at).toLocaleString('pt-BR')}</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="removeFavorite('${fav.parameter_name}')" title="Remover dos favoritos">
                        <i class="bi bi-star-fill"></i>
                    </button>
                    <button class="btn btn-sm btn-success" onclick="viewParameterValue('${fav.parameter_name}')" title="Ver Valor">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-info" onclick="viewHistory('${fav.parameter_name}')" title="Histórico">
                        <i class="bi bi-clock-history"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table></div>';
    favoritesContainer.innerHTML = html;
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
        fav.parameter_name.toLowerCase().includes(filter) ||
        (fav.alias && fav.alias.toLowerCase().includes(filter))
    );
    
    displayFavorites(filtered);
}

/**
 * Adiciona/Remove favorito (toggle sem confirmação)
 */
async function toggleFavorite(parameterName) {
    try {
        // Encode completo para usar na URL
        const encoded = encodeURIComponent(parameterName);
        
        // Verifica se já é favorito
        const checkResponse = await fetch(`/parameters/favorites/check/${encoded}`);
        const checkResult = await checkResponse.json();
        
        if (checkResult.is_favorite) {
            // Remove sem confirmação
            const response = await fetch(`/parameters/favorites/${encoded}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.success) {
                showAlert(result.message, 'success');
                loadFavorites();
                loadParameters(); // Atualiza a lista principal
            } else {
                showAlert(result.message, 'danger');
            }
        } else {
            // Adiciona
            const response = await fetch('/parameters/favorites', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    parameter_name: parameterName
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                showAlert(result.message, 'success');
                loadFavorites();
                loadParameters(); // Atualiza a lista principal
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
async function removeFavorite(parameterName) {
    if (!confirm(`Remover "${parameterName}" dos favoritos?`)) {
        return;
    }
    
    try {
        // Encode completo para preservar caracteres especiais
        const encoded = encodeURIComponent(parameterName);
        const response = await fetch(`/parameters/favorites/${encoded}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            loadFavorites();
            loadParameters(); // Atualiza a lista principal também
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}
