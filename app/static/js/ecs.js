// JavaScript para gerenciar ECS Clusters e Serviços

// Elementos do DOM
const clustersContainer = document.getElementById('clustersContainer');
const servicesContainer = document.getElementById('servicesContainer');
const tasksContainer = document.getElementById('tasksContainer');
const alertContainer = document.getElementById('alertContainer');
const servicesSection = document.getElementById('servicesSection');
const tasksSection = document.getElementById('tasksSection');
const selectedClusterNameSpan = document.getElementById('selectedClusterName');

// Variável global para armazenar o cluster selecionado
let currentCluster = null;
let allClusters = [];
let favoriteClusters = [];

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    loadClusters();
});

document.getElementById('refreshClustersBtn').addEventListener('click', () => {
    loadClusters();
});

document.getElementById('filterClusterName').addEventListener('input', () => {
    filterClusters();
});

document.getElementById('showOnlyFavorites').addEventListener('change', () => {
    filterClusters();
});

document.getElementById('refreshServicesBtn').addEventListener('click', () => {
    if (currentCluster) {
        loadServices(currentCluster);
    }
});

document.getElementById('viewTasksBtn').addEventListener('click', () => {
    if (currentCluster) {
        loadTasks(currentCluster);
    }
});

document.getElementById('closeTasksBtn').addEventListener('click', () => {
    tasksSection.style.display = 'none';
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
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

/**
 * Carrega a lista de clusters ECS
 */
async function loadClusters() {
    clustersContainer.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
            <p class="mt-2">Carregando clusters...</p>
        </div>
    `;
    
    try {
        // Carrega clusters
        const response = await fetch('/ecs/clusters');
        const result = await response.json();
        
        if (result.success) {
            allClusters = result.clusters;
            
            // Carrega favoritos
            const favResponse = await fetch('/ecs/favorites');
            const favResult = await favResponse.json();
            
            if (favResult.success) {
                favoriteClusters = favResult.favorites.map(f => f.cluster_name);
            }
            
            filterClusters();
        } else {
            clustersContainer.innerHTML = `
                <div class="alert alert-warning">
                    <i class="bi bi-exclamation-triangle"></i> ${result.message}
                </div>
            `;
        }
        
    } catch (error) {
        clustersContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-x-circle"></i> Erro ao carregar clusters: ${error.message}
            </div>
        `;
    }
}

/**
 * Filtra clusters por nome e favoritos
 */
function filterClusters() {
    const searchTerm = document.getElementById('filterClusterName').value.toLowerCase();
    const showOnlyFavorites = document.getElementById('showOnlyFavorites').checked;
    
    let filtered = allClusters;
    
    // Filtro por nome
    if (searchTerm) {
        filtered = filtered.filter(cluster => 
            cluster.name.toLowerCase().includes(searchTerm)
        );
    }
    
    // Filtro por favoritos
    if (showOnlyFavorites) {
        filtered = filtered.filter(cluster => 
            favoriteClusters.includes(cluster.name)
        );
    }
    
    displayClusters(filtered);
}

/**
 * Exibe a lista de clusters
 */
function displayClusters(clusters) {
    if (!clusters || clusters.length === 0) {
        clustersContainer.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-inbox"></i>
                <h5>Nenhum cluster encontrado</h5>
                <p class="text-muted">Não há clusters ECS na região configurada.</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    clusters.forEach(cluster => {
        const statusColor = cluster.status === 'ACTIVE' ? 'success' : 'warning';
        const isFavorite = favoriteClusters.includes(cluster.name);
        const starIcon = isFavorite ? 'bi-star-fill text-warning' : 'bi-star';
        
        html += `
            <div class="card cluster-card mb-3" onclick="selectCluster('${cluster.name}')">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center">
                            <div class="me-3">
                                <h5 class="mb-0">
                                    <i class="bi bi-server"></i> ${cluster.name}
                                </h5>
                                <span class="badge bg-${statusColor} mt-1">${cluster.status}</span>
                            </div>
                        </div>
                        
                        <div class="d-flex align-items-center">
                            <div class="d-flex text-center me-4">
                                <div class="metric me-4">
                                    <div class="metric-value text-primary">${cluster.active_services}</div>
                                    <div class="metric-label">Serviços</div>
                                </div>
                                <div class="metric me-4">
                                    <div class="metric-value text-success">${cluster.running_tasks}</div>
                                    <div class="metric-label">Tasks Rodando</div>
                                </div>
                                <div class="metric me-4">
                                    <div class="metric-value text-warning">${cluster.pending_tasks}</div>
                                    <div class="metric-label">Tasks Pendentes</div>
                                </div>
                            </div>
                            
                            <div class="btn-group btn-group-sm" role="group">
                                <button class="btn btn-outline-warning" onclick="event.stopPropagation(); toggleFavorite('${cluster.name}')" title="${isFavorite ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}">
                                    <i class="bi ${starIcon}"></i>
                                </button>
                                <button class="btn btn-outline-info" onclick="event.stopPropagation(); viewClusterDetails('${cluster.name}')">
                                    <i class="bi bi-info-circle"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    clustersContainer.innerHTML = html;
}

/**
 * Seleciona um cluster e carrega seus serviços
 */
function selectCluster(clusterName) {
    currentCluster = clusterName;
    selectedClusterNameSpan.textContent = clusterName;
    
    // Remove seleção anterior
    document.querySelectorAll('.cluster-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Adiciona seleção ao cluster clicado
    event.currentTarget.classList.add('selected');
    
    servicesSection.style.display = 'block';
    tasksSection.style.display = 'none';
    loadServices(clusterName);
    
    // Scroll suave para a seção de serviços
    setTimeout(() => {
        servicesSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

/**
 * Carrega os serviços de um cluster
 */
async function loadServices(clusterName) {
    servicesContainer.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-success" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
            <p class="mt-2">Carregando serviços...</p>
        </div>
    `;
    
    try {
        const response = await fetch(`/ecs/clusters/${clusterName}/services`);
        const result = await response.json();
        
        if (result.success) {
            displayServices(result.services, clusterName);
        } else {
            servicesContainer.innerHTML = `
                <div class="alert alert-warning">
                    <i class="bi bi-exclamation-triangle"></i> ${result.message}
                </div>
            `;
        }
        
    } catch (error) {
        servicesContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-x-circle"></i> Erro ao carregar serviços: ${error.message}
            </div>
        `;
    }
}

/**
 * Exibe a lista de serviços
 */
function displayServices(services, clusterName) {
    if (!services || services.length === 0) {
        servicesContainer.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-inbox"></i>
                <h5>Nenhum serviço encontrado</h5>
                <p class="text-muted">Este cluster não possui serviços ativos.</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="row">';
    
    services.forEach(service => {
        const statusColor = service.status === 'ACTIVE' ? 'success' : 'warning';
        const healthColor = service.running_count === service.desired_count ? 'success' : 'warning';
        const isRunning = service.running_count > 0;
        const serviceState = isRunning ? 'running' : 'stopped';
        
        html += `
            <div class="col-md-6 mb-3">
                <div class="card service-card ${serviceState}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <div>
                                <h5 class="card-title mb-1">
                                    <i class="bi bi-box"></i> ${service.name}
                                </h5>
                                <span class="badge bg-${statusColor}">${service.status}</span>
                                <span class="badge bg-secondary ms-1">${service.launch_type}</span>
                            </div>
                            <div class="btn-group btn-group-sm" role="group">
                                ${isRunning ? `
                                    <button class="btn btn-outline-danger" onclick="confirmStopService('${clusterName}', '${service.name}')" title="Parar Serviço">
                                        <i class="bi bi-stop-circle"></i>
                                    </button>
                                ` : `
                                    <button class="btn btn-outline-success" onclick="showStartServiceModal('${clusterName}', '${service.name}')" title="Iniciar Serviço">
                                        <i class="bi bi-play-circle"></i>
                                    </button>
                                `}
                                <button class="btn btn-outline-warning" onclick="showChangeCapacityModal('${clusterName}', '${service.name}', '${service.launch_type}')" title="Mudar Capacity Provider">
                                    <i class="bi bi-arrow-left-right"></i>
                                </button>
                                <button class="btn btn-outline-info" onclick="viewServiceDetails('${clusterName}', '${service.name}')" title="Ver Detalhes">
                                    <i class="bi bi-info-circle"></i>
                                </button>
                            </div>
                        </div>
                        
                        <div class="row text-center">
                            <div class="col-4">
                                <div class="metric">
                                    <div class="metric-value text-secondary">${service.desired_count}</div>
                                    <div class="metric-label">Desired</div>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="metric">
                                    <div class="metric-value text-${healthColor}">${service.running_count}</div>
                                    <div class="metric-label">Running</div>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="metric">
                                    <div class="metric-value text-warning">${service.pending_count}</div>
                                    <div class="metric-label">Pending</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-3">
                            <small class="text-muted">
                                <i class="bi bi-file-code"></i> Task Definition: <code>${service.task_definition}</code>
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    servicesContainer.innerHTML = html;
}

/**
 * Carrega as tasks de um cluster
 */
async function loadTasks(clusterName) {
    tasksSection.style.display = 'block';
    tasksContainer.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-info" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
            <p class="mt-2">Carregando tasks...</p>
        </div>
    `;
    
    // Scroll para a seção de tasks
    tasksSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    try {
        const response = await fetch(`/ecs/clusters/${clusterName}/tasks`);
        const result = await response.json();
        
        if (result.success) {
            displayTasks(result.tasks);
        } else {
            tasksContainer.innerHTML = `
                <div class="alert alert-warning">
                    <i class="bi bi-exclamation-triangle"></i> ${result.message}
                </div>
            `;
        }
        
    } catch (error) {
        tasksContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-x-circle"></i> Erro ao carregar tasks: ${error.message}
            </div>
        `;
    }
}

/**
 * Exibe a lista de tasks
 */
function displayTasks(tasks) {
    if (!tasks || tasks.length === 0) {
        tasksContainer.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-inbox"></i>
                <h5>Nenhuma task encontrada</h5>
                <p class="text-muted">Não há tasks em execução neste cluster.</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="table-responsive"><table class="table table-hover table-sm">';
    html += `
        <thead>
            <tr>
                <th>Task ID</th>
                <th>Status</th>
                <th>Launch Type</th>
                <th>Task Definition</th>
                <th>CPU</th>
                <th>Memory</th>
                <th>Containers</th>
                <th>Health</th>
            </tr>
        </thead>
        <tbody>
    `;
    
    tasks.forEach(task => {
        const statusColor = task.status === 'RUNNING' ? 'success' : 'warning';
        const healthColor = task.health_status === 'HEALTHY' ? 'success' : 
                           task.health_status === 'UNHEALTHY' ? 'danger' : 'secondary';
        
        html += `
            <tr>
                <td><code>${task.task_id.substring(0, 12)}</code></td>
                <td><span class="badge bg-${statusColor}">${task.status}</span></td>
                <td>${task.launch_type}</td>
                <td><small>${task.task_definition}</small></td>
                <td>${task.cpu}</td>
                <td>${task.memory}</td>
                <td>${task.containers}</td>
                <td><span class="badge bg-${healthColor}">${task.health_status}</span></td>
            </tr>
        `;
    });
    
    html += '</tbody></table></div>';
    tasksContainer.innerHTML = html;
}

/**
 * Visualiza detalhes de um cluster
 */
async function viewClusterDetails(clusterName) {
    // Implementação futura - pode mostrar mais detalhes em um modal
    showAlert(`Detalhes do cluster: ${clusterName}`, 'info');
}

/**
 * Visualiza detalhes de um serviço
 */
async function viewServiceDetails(clusterName, serviceName) {
    // Implementação futura - pode mostrar mais detalhes em um modal
    showAlert(`Detalhes do serviço: ${serviceName}`, 'info');
}

/**
 * Confirma e para um serviço
 */
function confirmStopService(clusterName, serviceName) {
    if (confirm(`Tem certeza que deseja PARAR o serviço "${serviceName}"?\n\nIsso irá definir o desiredCount para 0 e todas as tasks serão encerradas.`)) {
        stopService(clusterName, serviceName);
    }
}

/**
 * Para um serviço ECS
 */
async function stopService(clusterName, serviceName) {
    try {
        showAlert(`Parando serviço ${serviceName}...`, 'info');
        
        const response = await fetch(`/ecs/clusters/${clusterName}/services/${serviceName}/stop`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            // Recarrega a lista de serviços
            setTimeout(() => loadServices(clusterName), 2000);
        } else {
            showAlert(result.message, 'danger');
        }
        
    } catch (error) {
        showAlert(`Erro ao parar serviço: ${error.message}`, 'danger');
    }
}

/**
 * Mostra modal para iniciar serviço
 */
function showStartServiceModal(clusterName, serviceName) {
    const desiredCount = prompt(`Quantas tasks deseja iniciar para o serviço "${serviceName}"?`, '1');
    
    if (desiredCount !== null && desiredCount.trim() !== '') {
        startService(clusterName, serviceName, parseInt(desiredCount));
    }
}

/**
 * Inicia um serviço ECS
 */
async function startService(clusterName, serviceName, desiredCount) {
    try {
        showAlert(`Iniciando serviço ${serviceName} com ${desiredCount} task(s)...`, 'info');
        
        const response = await fetch(`/ecs/clusters/${clusterName}/services/${serviceName}/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ desired_count: desiredCount })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            // Recarrega a lista de serviços
            setTimeout(() => loadServices(clusterName), 2000);
        } else {
            showAlert(result.message, 'danger');
        }
        
    } catch (error) {
        showAlert(`Erro ao iniciar serviço: ${error.message}`, 'danger');
    }
}

/**
 * Adiciona ou remove cluster dos favoritos
 */
async function toggleFavorite(clusterName) {
    const isFavorite = favoriteClusters.includes(clusterName);
    
    try {
        if (isFavorite) {
            // Remove dos favoritos
            const response = await fetch(`/ecs/favorites/${encodeURIComponent(clusterName)}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.success) {
                favoriteClusters = favoriteClusters.filter(name => name !== clusterName);
                showAlert(`Cluster "${clusterName}" removido dos favoritos`, 'success');
                filterClusters();
            } else {
                showAlert(result.message, 'danger');
            }
        } else {
            // Adiciona aos favoritos
            const response = await fetch(`/ecs/favorites/${encodeURIComponent(clusterName)}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });
            
            const result = await response.json();
            
            if (result.success) {
                favoriteClusters.push(clusterName);
                showAlert(`Cluster "${clusterName}" adicionado aos favoritos`, 'success');
                filterClusters();
            } else {
                showAlert(result.message, 'danger');
            }
        }
    } catch (error) {
        showAlert(`Erro ao atualizar favorito: ${error.message}`, 'danger');
    }
}

/**
 * Mostra modal para mudar capacity provider
 */
function showChangeCapacityModal(clusterName, serviceName, currentLaunchType) {
    const options = ['FARGATE', 'FARGATE_SPOT'];
    const currentIndex = options.indexOf(currentLaunchType);
    const newProvider = options[1 - currentIndex]; // Alterna entre os dois
    
    const message = `Deseja alterar o Capacity Provider do serviço "${serviceName}"?\n\n` +
                   `Atual: ${currentLaunchType}\n` +
                   `Novo: ${newProvider}\n\n` +
                   `Isso irá forçar um novo deployment do serviço.`;
    
    if (confirm(message)) {
        changeCapacityProvider(clusterName, serviceName, newProvider);
    }
}

/**
 * Altera o capacity provider de um serviço
 */
async function changeCapacityProvider(clusterName, serviceName, capacityProvider) {
    try {
        showAlert(`Alterando Capacity Provider para ${capacityProvider}...`, 'info');
        
        const response = await fetch(`/ecs/clusters/${clusterName}/services/${serviceName}/change-capacity`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ capacity_provider: capacityProvider })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message + ' - Aguarde o deployment...', 'success');
            // Recarrega a lista de serviços
            setTimeout(() => loadServices(clusterName), 3000);
        } else {
            showAlert(result.message, 'danger');
        }
        
    } catch (error) {
        showAlert(`Erro ao alterar capacity provider: ${error.message}`, 'danger');
    }
}
