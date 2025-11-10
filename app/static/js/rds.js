// JavaScript para gerenciar RDS Instances

// Elementos do DOM
const instancesContainer = document.getElementById('instancesContainer');
const alertContainer = document.getElementById('alertContainer');
const createInstanceBtn = document.getElementById('createInstanceBtn');
const refreshInstancesBtn = document.getElementById('refreshInstancesBtn');

// Variáveis globais
let allInstances = [];
let favoriteInstances = [];

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    loadInstances();
});

refreshInstancesBtn.addEventListener('click', () => {
    loadInstances();
});

createInstanceBtn.addEventListener('click', () => {
    createInstance();
});

document.getElementById('filterInstanceName').addEventListener('input', () => {
    filterInstances();
});

document.getElementById('showOnlyFavorites').addEventListener('change', () => {
    filterInstances();
});

/**
 * Exibe um alerta na página
 */
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    
    alertDiv.innerHTML = `
        <strong>${type === 'success' ? 'Sucesso!' : type === 'danger' ? 'Erro!' : 'Atenção!'}</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.innerHTML = '';
    alertContainer.appendChild(alertDiv);
    
    // Scroll para o topo
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    setTimeout(() => {
        alertDiv.remove();
    }, 8000);
}

/**
 * Carrega a lista de instâncias RDS
 */
async function loadInstances() {
    instancesContainer.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
            <p class="mt-2">Carregando instâncias...</p>
        </div>
    `;
    
    try {
        // Carrega instâncias
        const response = await fetch('/rds/instances');
        const result = await response.json();
        
        if (result.success) {
            allInstances = result.instances;
            
            // Carrega favoritos
            const favResponse = await fetch('/rds/favorites');
            const favResult = await favResponse.json();
            
            if (favResult.success) {
                favoriteInstances = favResult.favorites.map(f => f.instance_identifier);
            }
            
            filterInstances();
        } else {
            instancesContainer.innerHTML = `
                <div class="alert alert-warning">
                    <i class="bi bi-exclamation-triangle"></i> ${result.message}
                </div>
            `;
        }
        
    } catch (error) {
        instancesContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-x-circle"></i> Erro ao carregar instâncias: ${error.message}
            </div>
        `;
    }
}

/**
 * Filtra instâncias por nome e favoritos
 */
function filterInstances() {
    const searchTerm = document.getElementById('filterInstanceName').value.toLowerCase();
    const showOnlyFavorites = document.getElementById('showOnlyFavorites').checked;
    
    let filtered = allInstances;
    
    // Filtro por nome
    if (searchTerm) {
        filtered = filtered.filter(instance => 
            instance.db_instance_identifier.toLowerCase().includes(searchTerm)
        );
    }
    
    // Filtro por favoritos
    if (showOnlyFavorites) {
        filtered = filtered.filter(instance => 
            favoriteInstances.includes(instance.db_instance_identifier)
        );
    }
    
    displayInstances(filtered);
}

/**
 * Exibe a lista de instâncias
 */
function displayInstances(instances) {
    if (!instances || instances.length === 0) {
        instancesContainer.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-inbox"></i>
                <h5>Nenhuma instância encontrada</h5>
                <p class="text-muted">Crie sua primeira instância RDS clicando no botão acima.</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="table-responsive"><table class="table table-hover">';
    html += `
        <thead>
            <tr>
                <th>Identificador</th>
                <th>Status</th>
                <th>Engine</th>
                <th>Classe</th>
                <th>Storage</th>
                <th>Multi-AZ</th>
                <th>Endpoint</th>
                <th>Ações</th>
            </tr>
        </thead>
        <tbody>
    `;
    
    instances.forEach(instance => {
        const statusColor = getStatusColor(instance.status);
        const isAvailable = instance.status === 'available';
        const isStopped = instance.status === 'stopped';
        const isFavorite = favoriteInstances.includes(instance.db_instance_identifier);
        const starIcon = isFavorite ? 'bi-star-fill text-warning' : 'bi-star';
        
        html += `
            <tr>
                <td>
                    <strong>${instance.identifier}</strong>
                    <button class="btn btn-sm btn-link p-0 ms-2" onclick="toggleFavorite('${instance.db_instance_identifier}')" title="${isFavorite ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}">
                        <i class="bi ${starIcon}"></i>
                    </button>
                </td>
                <td><span class="badge bg-${statusColor}">${instance.status}</span></td>
                <td>
                    <i class="bi bi-database"></i> ${instance.engine}
                    <br><small class="text-muted">${instance.engine_version}</small>
                </td>
                <td>${instance.instance_class}</td>
                <td>${instance.storage} GB<br><small class="text-muted">${instance.storage_type}</small></td>
                <td>${instance.multi_az ? '<span class="badge bg-success">Sim</span>' : '<span class="badge bg-secondary">Não</span>'}</td>
                <td>
                    ${instance.endpoint !== 'N/A' ? `
                        <small><code>${instance.endpoint}:${instance.port}</code></small>
                        <button class="btn btn-sm btn-link" onclick="copyToClipboard('${instance.endpoint}')">
                            <i class="bi bi-clipboard"></i>
                        </button>
                    ` : '<span class="text-muted">-</span>'}
                </td>
                <td>
                    <div class="btn-group btn-group-sm" role="group">
                        ${isAvailable ? `
                            <button class="btn btn-outline-warning" onclick="confirmStopInstance('${instance.identifier}')" title="Parar Instância">
                                <i class="bi bi-stop-circle"></i>
                            </button>
                        ` : ''}
                        ${isStopped ? `
                            <button class="btn btn-outline-success" onclick="confirmStartInstance('${instance.identifier}')" title="Iniciar Instância">
                                <i class="bi bi-play-circle"></i>
                            </button>
                        ` : ''}
                        <button class="btn btn-outline-info" onclick="viewInstanceDetails('${instance.identifier}')" title="Ver Detalhes">
                            <i class="bi bi-info-circle"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="confirmDeleteInstance('${instance.identifier}')" title="Deletar Instância">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table></div>';
    instancesContainer.innerHTML = html;
}

/**
 * Retorna a cor do badge baseado no status
 */
function getStatusColor(status) {
    const colors = {
        'available': 'success',
        'creating': 'info',
        'modifying': 'warning',
        'backing-up': 'info',
        'stopped': 'secondary',
        'stopping': 'warning',
        'starting': 'info',
        'deleting': 'danger',
        'failed': 'danger'
    };
    return colors[status] || 'secondary';
}

/**
 * Cria uma nova instância RDS
 */
async function createInstance() {
    const form = document.getElementById('createInstanceForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const data = {
        db_instance_identifier: document.getElementById('dbInstanceIdentifier').value,
        db_instance_class: document.getElementById('dbInstanceClass').value,
        engine: document.getElementById('engine').value,
        master_username: document.getElementById('masterUsername').value,
        master_password: document.getElementById('masterPassword').value,
        allocated_storage: parseInt(document.getElementById('allocatedStorage').value),
        db_name: document.getElementById('dbName').value || null,
        publicly_accessible: document.getElementById('publiclyAccessible').checked,
        multi_az: document.getElementById('multiAZ').checked
    };
    
    createInstanceBtn.disabled = true;
    createInstanceBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Criando...';
    
    try {
        const response = await fetch('/rds/instances', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message + ' - A instância levará alguns minutos para ficar disponível.', 'success');
            
            // Fecha o modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('createInstanceModal'));
            modal.hide();
            
            // Limpa o formulário
            form.reset();
            
            // Recarrega a lista
            setTimeout(() => loadInstances(), 2000);
        } else {
            showAlert(result.message, 'danger');
        }
        
    } catch (error) {
        showAlert(`Erro ao criar instância: ${error.message}`, 'danger');
    } finally {
        createInstanceBtn.disabled = false;
        createInstanceBtn.innerHTML = '<i class="bi bi-plus-circle"></i> Criar Instância';
    }
}

/**
 * Confirma e para uma instância
 */
function confirmStopInstance(identifier) {
    if (confirm(`Tem certeza que deseja PARAR a instância "${identifier}"?\n\nIsso irá parar o banco de dados e você não será cobrado por computação, apenas por storage.`)) {
        stopInstance(identifier);
    }
}

/**
 * Para uma instância RDS
 */
async function stopInstance(identifier) {
    try {
        showAlert(`Parando instância ${identifier}...`, 'info');
        
        const response = await fetch(`/rds/instances/${identifier}/stop`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            setTimeout(() => loadInstances(), 2000);
        } else {
            showAlert(result.message, 'danger');
        }
        
    } catch (error) {
        showAlert(`Erro ao parar instância: ${error.message}`, 'danger');
    }
}

/**
 * Confirma e inicia uma instância
 */
function confirmStartInstance(identifier) {
    if (confirm(`Deseja INICIAR a instância "${identifier}"?`)) {
        startInstance(identifier);
    }
}

/**
 * Inicia uma instância RDS
 */
async function startInstance(identifier) {
    try {
        showAlert(`Iniciando instância ${identifier}...`, 'info');
        
        const response = await fetch(`/rds/instances/${identifier}/start`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            setTimeout(() => loadInstances(), 2000);
        } else {
            showAlert(result.message, 'danger');
        }
        
    } catch (error) {
        showAlert(`Erro ao iniciar instância: ${error.message}`, 'danger');
    }
}

/**
 * Confirma e deleta uma instância
 */
function confirmDeleteInstance(identifier) {
    const skipSnapshot = confirm(
        `ATENÇÃO: Você está prestes a DELETAR a instância "${identifier}"!\n\n` +
        `Clique em OK para criar um snapshot final (recomendado)\n` +
        `Clique em CANCELAR para abortar a operação`
    );
    
    if (skipSnapshot !== null) {
        const finalConfirm = confirm(
            `Confirma a EXCLUSÃO da instância "${identifier}"?\n\n` +
            `${skipSnapshot ? 'COM' : 'SEM'} snapshot final\n\n` +
            `Esta ação NÃO pode ser desfeita!`
        );
        
        if (finalConfirm) {
            deleteInstance(identifier, !skipSnapshot);
        }
    }
}

/**
 * Deleta uma instância RDS
 */
async function deleteInstance(identifier, skipSnapshot) {
    try {
        showAlert(`Deletando instância ${identifier}...`, 'info');
        
        const response = await fetch(`/rds/instances/${identifier}?skip_final_snapshot=${skipSnapshot}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            setTimeout(() => loadInstances(), 2000);
        } else {
            showAlert(result.message, 'danger');
        }
        
    } catch (error) {
        showAlert(`Erro ao deletar instância: ${error.message}`, 'danger');
    }
}

/**
 * Visualiza detalhes de uma instância
 */
async function viewInstanceDetails(identifier) {
    const modal = new bootstrap.Modal(document.getElementById('instanceDetailsModal'));
    const modalBody = document.getElementById('instanceDetailsBody');
    
    modalBody.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
        </div>
    `;
    
    modal.show();
    
    try {
        const response = await fetch(`/rds/instances/${identifier}`);
        const result = await response.json();
        
        if (result.success) {
            const instance = result.instance;
            
            modalBody.innerHTML = `
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <strong>Identificador:</strong><br>
                        ${instance.identifier}
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>Status:</strong><br>
                        <span class="badge bg-${getStatusColor(instance.status)}">${instance.status}</span>
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>Engine:</strong><br>
                        ${instance.engine} ${instance.engine_version}
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>Classe:</strong><br>
                        ${instance.instance_class}
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>Storage:</strong><br>
                        ${instance.storage} GB (${instance.storage_type})
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>Multi-AZ:</strong><br>
                        ${instance.multi_az ? 'Sim' : 'Não'}
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>Acesso Público:</strong><br>
                        ${instance.publicly_accessible ? 'Sim' : 'Não'}
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>Backup Retention:</strong><br>
                        ${instance.backup_retention} dias
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>Master Username:</strong><br>
                        ${instance.master_username}
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>Nome do Banco:</strong><br>
                        ${instance.db_name}
                    </div>
                    <div class="col-md-12 mb-3">
                        <strong>Endpoint:</strong><br>
                        ${instance.endpoint !== 'N/A' ? `
                            <code>${instance.endpoint}:${instance.port}</code>
                            <button class="btn btn-sm btn-outline-secondary" onclick="copyToClipboard('${instance.endpoint}')">
                                <i class="bi bi-clipboard"></i> Copiar
                            </button>
                        ` : '<span class="text-muted">Não disponível</span>'}
                    </div>
                </div>
            `;
        } else {
            modalBody.innerHTML = `
                <div class="alert alert-danger">
                    ${result.message}
                </div>
            `;
        }
        
    } catch (error) {
        modalBody.innerHTML = `
            <div class="alert alert-danger">
                Erro ao carregar detalhes: ${error.message}
            </div>
        `;
    }
}

/**
 * Copia texto para a área de transferência
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('Endpoint copiado para a área de transferência!', 'success');
    }).catch(err => {
        showAlert('Erro ao copiar: ' + err, 'danger');
    });
}

/**
 * Adiciona ou remove instância dos favoritos
 */
async function toggleFavorite(instanceIdentifier) {
    const isFavorite = favoriteInstances.includes(instanceIdentifier);
    
    try {
        if (isFavorite) {
            // Remove dos favoritos
            const response = await fetch(`/rds/favorites/${encodeURIComponent(instanceIdentifier)}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.success) {
                favoriteInstances = favoriteInstances.filter(name => name !== instanceIdentifier);
                showAlert(`Instância "${instanceIdentifier}" removida dos favoritos`, 'success');
                filterInstances();
            } else {
                showAlert(result.message, 'danger');
            }
        } else {
            // Adiciona aos favoritos
            const response = await fetch(`/rds/favorites/${encodeURIComponent(instanceIdentifier)}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });
            
            const result = await response.json();
            
            if (result.success) {
                favoriteInstances.push(instanceIdentifier);
                showAlert(`Instância "${instanceIdentifier}" adicionada aos favoritos`, 'success');
                filterInstances();
            } else {
                showAlert(result.message, 'danger');
            }
        }
    } catch (error) {
        showAlert(`Erro ao atualizar favorito: ${error.message}`, 'danger');
    }
}
