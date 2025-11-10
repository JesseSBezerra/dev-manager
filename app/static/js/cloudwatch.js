// JavaScript para CloudWatch Logs

const alertContainer = document.getElementById('alertContainer');
const logGroupsContainer = document.getElementById('logGroupsContainer');
const favoritesContainer = document.getElementById('favoritesContainer');
const queryResultsContainer = document.getElementById('queryResultsContainer');
const refreshLogGroupsBtn = document.getElementById('refreshLogGroupsBtn');
const refreshFavoritesBtn = document.getElementById('refreshFavoritesBtn');
const executeQueryBtn = document.getElementById('executeQueryBtn');
const clearQueryBtn = document.getElementById('clearQueryBtn');
const logGroupFilter = document.getElementById('logGroupFilter');
const clearFilterBtn = document.getElementById('clearFilterBtn');
const favoritesFilter = document.getElementById('favoritesFilter');
const clearFavoritesFilterBtn = document.getElementById('clearFavoritesFilterBtn');
const savedQueriesSelect = document.getElementById('savedQueriesSelect');
const refreshSavedQueriesBtn = document.getElementById('refreshSavedQueriesBtn');
const saveQueryBtn = document.getElementById('saveQueryBtn');

let allLogGroups = [];
let allFavorites = [];
let currentLogGroupName = null;

// Event Listeners
refreshLogGroupsBtn.addEventListener('click', loadLogGroups);
refreshFavoritesBtn.addEventListener('click', loadFavorites);
executeQueryBtn.addEventListener('click', executeInsightsQuery);
clearQueryBtn.addEventListener('click', clearQuery);
logGroupFilter.addEventListener('input', filterLogGroups);
clearFilterBtn.addEventListener('click', () => {
    logGroupFilter.value = '';
    filterLogGroups();
});
favoritesFilter.addEventListener('input', filterFavorites);
clearFavoritesFilterBtn.addEventListener('click', () => {
    favoritesFilter.value = '';
    filterFavorites();
});
savedQueriesSelect.addEventListener('change', loadSavedQuery);
refreshSavedQueriesBtn.addEventListener('click', loadSavedQueriesForLogGroup);
saveQueryBtn.addEventListener('click', saveCurrentQuery);

// Carregar ao iniciar
document.addEventListener('DOMContentLoaded', () => {
    loadLogGroups();
    loadLogGroupsForInsights();
    loadFavorites();
});

// Atualizar lista de log groups quando trocar para aba Insights
document.getElementById('insights-tab').addEventListener('shown.bs.tab', loadLogGroupsForInsights);

// Atualizar favoritos quando trocar para aba Favoritos
document.getElementById('favorites-tab').addEventListener('shown.bs.tab', loadFavorites);

// Carregar streams quando selecionar log stream
document.getElementById('streamSelect')?.addEventListener('change', (e) => {
    if (e.target.value) {
        loadLogEvents(currentLogGroupName, e.target.value);
    }
});

// Carregar queries salvas quando selecionar log group no Insights
document.getElementById('insightsLogGroups').addEventListener('change', loadSavedQueriesForLogGroup);

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
 * Carrega lista de log groups
 */
async function loadLogGroups() {
    logGroupsContainer.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2">Carregando log groups...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/cloudwatch/log-groups');
        const result = await response.json();
        
        if (result.success) {
            allLogGroups = result.log_groups;
            displayLogGroups(allLogGroups);
        } else {
            logGroupsContainer.innerHTML = `
                <div class="alert alert-danger">
                    ${result.message}
                </div>
            `;
        }
    } catch (error) {
        logGroupsContainer.innerHTML = `
            <div class="alert alert-danger">
                Erro ao carregar log groups: ${error.message}
            </div>
        `;
    }
}

/**
 * Exibe lista de log groups
 */
function displayLogGroups(logGroups) {
    if (logGroups.length === 0) {
        logGroupsContainer.innerHTML = `
            <div class="text-center text-muted">
                <i class="bi bi-inbox" style="font-size: 3rem;"></i>
                <p class="mt-2">Nenhum log group encontrado</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="list-group">';
    
    logGroups.forEach(group => {
        const sizeInMB = (group.stored_bytes / (1024 * 1024)).toFixed(2);
        const creationDate = new Date(group.creation_time).toLocaleString('pt-BR');
        
        html += `
            <div class="list-group-item list-group-item-action">
                <div class="d-flex w-100 justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="mb-1">
                            <i class="bi bi-folder text-primary"></i>
                            <strong>${group.name}</strong>
                        </h6>
                        <p class="mb-1 small text-muted">
                            <i class="bi bi-calendar"></i> Criado: ${creationDate} |
                            <i class="bi bi-hdd"></i> Tamanho: ${sizeInMB} MB |
                            <i class="bi bi-clock"></i> Retenção: ${group.retention_days} dias
                        </p>
                    </div>
                    <div class="btn-group" role="group">
                        <button class="btn btn-sm btn-warning" onclick="toggleFavorite('${group.name}')" title="Adicionar aos favoritos" id="fav-${btoa(group.name)}">
                            <i class="bi bi-star"></i>
                        </button>
                        <button class="btn btn-sm btn-primary" onclick="viewLogStreams('${group.name}')" title="Ver Streams">
                            <i class="bi bi-file-text"></i> Streams
                        </button>
                        <button class="btn btn-sm btn-info" onclick="viewLogGroupDetails('${group.name}')" title="Detalhes">
                            <i class="bi bi-info-circle"></i>
                        </button>
                        <button class="btn btn-sm btn-success" onclick="useInInsights('${group.name}')" title="Usar no Insights">
                            <i class="bi bi-search"></i> Query
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    logGroupsContainer.innerHTML = html;
}

/**
 * Filtra log groups
 */
function filterLogGroups() {
    const filter = logGroupFilter.value.toLowerCase();
    
    if (!filter) {
        displayLogGroups(allLogGroups);
        return;
    }
    
    const filtered = allLogGroups.filter(group => 
        group.name.toLowerCase().includes(filter)
    );
    
    displayLogGroups(filtered);
}

/**
 * Visualiza log streams
 */
async function viewLogStreams(logGroupName) {
    // Decodifica o nome do log group caso venha encoded
    logGroupName = decodeURIComponent(logGroupName);
    currentLogGroupName = logGroupName;
    
    const modal = new bootstrap.Modal(document.getElementById('logStreamModal'));
    const streamSelect = document.getElementById('streamSelect');
    const modalLogGroupName = document.getElementById('modalLogGroupName');
    const logEventsContainer = document.getElementById('logEventsContainer');
    
    modalLogGroupName.textContent = logGroupName;
    streamSelect.innerHTML = '<option value="">Carregando...</option>';
    logEventsContainer.innerHTML = '<div class="text-center text-muted"><p>Selecione um stream</p></div>';
    
    modal.show();
    
    try {
        // Codifica corretamente para a URL, preservando as barras
        const encodedLogGroup = logGroupName.split('/').map(part => encodeURIComponent(part)).join('/');
        const response = await fetch(`/cloudwatch/log-groups/${encodedLogGroup}/streams`);
        const result = await response.json();
        
        if (result.success) {
            if (result.log_streams.length === 0) {
                streamSelect.innerHTML = '<option value="">Nenhum stream encontrado</option>';
            } else {
                streamSelect.innerHTML = '<option value="">Selecione um stream...</option>';
                result.log_streams.forEach(stream => {
                    const option = document.createElement('option');
                    option.value = stream.name;
                    const lastEvent = stream.last_event_time ? 
                        new Date(stream.last_event_time).toLocaleString('pt-BR') : 'N/A';
                    option.textContent = `${stream.name} (Último evento: ${lastEvent})`;
                    streamSelect.appendChild(option);
                });
            }
        } else {
            streamSelect.innerHTML = '<option value="">Erro ao carregar</option>';
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        streamSelect.innerHTML = '<option value="">Erro ao carregar</option>';
        console.error('Erro ao carregar streams:', error);
    }
}

/**
 * Carrega eventos de log
 */
async function loadLogEvents(logGroupName, logStreamName) {
    const container = document.getElementById('logEventsContainer');
    
    container.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-info" role="status"></div>
            <p class="mt-2">Carregando eventos...</p>
        </div>
    `;
    
    try {
        // Codifica corretamente preservando as barras
        const encodedLogGroup = logGroupName.split('/').map(part => encodeURIComponent(part)).join('/');
        const encodedLogStream = logStreamName.split('/').map(part => encodeURIComponent(part)).join('/');
        
        const response = await fetch(
            `/cloudwatch/log-groups/${encodedLogGroup}/streams/${encodedLogStream}/events?limit=100`
        );
        const result = await response.json();
        
        if (result.success) {
            displayLogEvents(result.events);
        } else {
            container.innerHTML = `<div class="alert alert-danger">${result.message}</div>`;
        }
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">Erro: ${error.message}</div>`;
    }
}

/**
 * Exibe eventos de log
 */
function displayLogEvents(events) {
    const container = document.getElementById('logEventsContainer');
    
    if (events.length === 0) {
        container.innerHTML = '<div class="alert alert-info">Nenhum evento encontrado</div>';
        return;
    }
    
    let html = `<div class="mb-2"><strong>${events.length} evento(s) encontrado(s)</strong></div>`;
    html += '<div style="max-height: 500px; overflow-y: auto;">';
    
    events.forEach(event => {
        const timestamp = new Date(event.timestamp).toLocaleString('pt-BR');
        html += `
            <div class="card mb-2">
                <div class="card-body p-2">
                    <div class="d-flex justify-content-between">
                        <small class="text-muted"><i class="bi bi-clock"></i> ${timestamp}</small>
                    </div>
                    <pre class="mb-0 mt-1" style="font-size: 0.85rem; white-space: pre-wrap;">${event.message}</pre>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

/**
 * Visualiza detalhes do log group
 */
async function viewLogGroupDetails(logGroupName) {
    // Decodifica o nome do log group caso venha encoded
    logGroupName = decodeURIComponent(logGroupName);
    
    const modal = new bootstrap.Modal(document.getElementById('logGroupDetailsModal'));
    const modalBody = document.getElementById('logGroupDetailsBody');
    
    modalBody.innerHTML = '<div class="text-center"><div class="spinner-border text-primary"></div></div>';
    modal.show();
    
    try {
        // Codifica corretamente preservando as barras
        const encodedLogGroup = logGroupName.split('/').map(part => encodeURIComponent(part)).join('/');
        const response = await fetch(`/cloudwatch/log-groups/${encodedLogGroup}`);
        const result = await response.json();
        
        if (result.success) {
            const group = result.log_group;
            const sizeInMB = (group.stored_bytes / (1024 * 1024)).toFixed(2);
            const creationDate = new Date(group.creation_time).toLocaleString('pt-BR');
            
            modalBody.innerHTML = `
                <table class="table table-bordered">
                    <tr><th>Nome</th><td class="font-monospace">${group.name}</td></tr>
                    <tr><th>ARN</th><td class="font-monospace small">${group.arn}</td></tr>
                    <tr><th>Criado em</th><td>${creationDate}</td></tr>
                    <tr><th>Retenção</th><td>${group.retention_days} dias</td></tr>
                    <tr><th>Tamanho Armazenado</th><td>${sizeInMB} MB</td></tr>
                    <tr><th>Filtros de Métrica</th><td>${group.metric_filter_count}</td></tr>
                    <tr><th>Criptografia KMS</th><td>${group.kms_key_id}</td></tr>
                </table>
            `;
        } else {
            modalBody.innerHTML = `<div class="alert alert-danger">${result.message}</div>`;
        }
    } catch (error) {
        modalBody.innerHTML = `<div class="alert alert-danger">Erro: ${error.message}</div>`;
    }
}

/**
 * Usa log group no Insights
 */
function useInInsights(logGroupName) {
    // Decodifica o nome do log group caso venha encoded
    logGroupName = decodeURIComponent(logGroupName);
    
    // Muda para aba Insights
    const insightsTab = new bootstrap.Tab(document.getElementById('insights-tab'));
    insightsTab.show();
    
    // Seleciona o log group
    const select = document.getElementById('insightsLogGroups');
    for (let option of select.options) {
        if (option.value === logGroupName) {
            option.selected = true;
            break;
        }
    }
}

/**
 * Carrega log groups para o Insights
 */
async function loadLogGroupsForInsights() {
    const select = document.getElementById('insightsLogGroups');
    select.innerHTML = '<option value="">Carregando...</option>';
    
    try {
        const response = await fetch('/cloudwatch/log-groups');
        const result = await response.json();
        
        if (result.success) {
            select.innerHTML = '';
            result.log_groups.forEach(group => {
                const option = document.createElement('option');
                option.value = group.name;
                option.textContent = group.name;
                select.appendChild(option);
            });
        } else {
            select.innerHTML = '<option value="">Erro ao carregar</option>';
        }
    } catch (error) {
        select.innerHTML = '<option value="">Erro ao carregar</option>';
    }
}

/**
 * Executa query no Insights
 */
async function executeInsightsQuery() {
    const select = document.getElementById('insightsLogGroups');
    const selectedGroups = Array.from(select.selectedOptions).map(opt => opt.value);
    const queryString = document.getElementById('insightsQuery').value.trim();
    const hoursAgo = parseInt(document.getElementById('insightsHours').value);
    const limit = parseInt(document.getElementById('insightsLimit').value);
    
    if (selectedGroups.length === 0) {
        showAlert('Selecione pelo menos um log group', 'warning');
        return;
    }
    
    if (!queryString) {
        showAlert('Digite uma query', 'warning');
        return;
    }
    
    executeQueryBtn.disabled = true;
    executeQueryBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Executando...';
    
    queryResultsContainer.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-success" role="status"></div>
            <p class="mt-2">Executando query...</p>
        </div>
    `;
    
    const startTime = Date.now();
    
    try {
        const response = await fetch('/cloudwatch/insights/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                log_group_names: selectedGroups,
                query_string: queryString,
                hours_ago: hoursAgo,
                limit: limit
            })
        });
        
        const result = await response.json();
        const executionTime = Date.now() - startTime;
        
        if (result.success) {
            displayQueryResults(result.results, executionTime, result.statistics);
            showAlert(`Query executada com sucesso em ${(executionTime/1000).toFixed(2)}s`, 'success');
        } else {
            queryResultsContainer.innerHTML = `<div class="alert alert-danger">${result.message}</div>`;
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        queryResultsContainer.innerHTML = `<div class="alert alert-danger">Erro: ${error.message}</div>`;
        showAlert(`Erro: ${error.message}`, 'danger');
    } finally {
        executeQueryBtn.disabled = false;
        executeQueryBtn.innerHTML = '<i class="bi bi-play-fill"></i> Executar Query';
    }
}

/**
 * Exibe resultados da query
 */
function displayQueryResults(results, executionTime, statistics) {
    if (results.length === 0) {
        queryResultsContainer.innerHTML = '<div class="alert alert-info">Nenhum resultado encontrado</div>';
        return;
    }
    
    let html = `
        <div class="mb-3">
            <span class="badge bg-success">${results.length} resultado(s)</span>
            <span class="badge bg-info">${(executionTime/1000).toFixed(2)}s</span>
        </div>
    `;
    
    // Extrai campos
    const fields = results[0].map(field => field.field);
    
    html += '<div class="table-responsive"><table class="table table-striped table-hover table-sm">';
    html += '<thead class="table-dark"><tr>';
    fields.forEach(field => {
        html += `<th>${field}</th>`;
    });
    html += '</tr></thead><tbody>';
    
    results.forEach(row => {
        html += '<tr>';
        row.forEach(field => {
            html += `<td>${field.value || '<span class="text-muted">null</span>'}</td>`;
        });
        html += '</tr>';
    });
    
    html += '</tbody></table></div>';
    queryResultsContainer.innerHTML = html;
}

/**
 * Limpa query
 */
function clearQuery() {
    document.getElementById('insightsQuery').value = '';
    queryResultsContainer.innerHTML = `
        <div class="text-center text-muted">
            <i class="bi bi-inbox" style="font-size: 3rem;"></i>
            <p class="mt-2">Execute uma query para ver os resultados aqui</p>
        </div>
    `;
}

/**
 * Insere template de query
 */
function insertQueryTemplate(type) {
    const queryInput = document.getElementById('insightsQuery');
    
    const templates = {
        'errors': `fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100`,
        
        'stats': `fields @timestamp
| stats count(*) as count by bin(5m)
| sort @timestamp desc`,
        
        'filter': `fields @timestamp, @message, @logStream
| filter @message like /pattern/
| sort @timestamp desc
| limit 100`,
        
        'slow': `fields @timestamp, @message, @duration
| filter @duration > 1000
| sort @duration desc
| limit 50`,
        
        'count': `fields @timestamp, statusCode
| stats count() by statusCode
| sort count() desc`
    };
    
    queryInput.value = templates[type] || '';
    queryInput.focus();
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
        const response = await fetch('/cloudwatch/favorites');
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
                <p class="mt-2">Nenhum log group favoritado ainda</p>
                <p class="small">Clique na estrela ⭐ em qualquer log group para adicionar aos favoritos</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="list-group">';
    
    favorites.forEach(fav => {
        html += `
            <div class="list-group-item list-group-item-action">
                <div class="d-flex w-100 justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="mb-1">
                            <i class="bi bi-star-fill text-warning"></i>
                            <strong>${fav.log_group_name}</strong>
                            ${fav.alias ? `<span class="badge bg-secondary ms-2">${fav.alias}</span>` : ''}
                        </h6>
                        <p class="mb-1 small text-muted">
                            <i class="bi bi-calendar"></i> Favoritado em: ${new Date(fav.created_at).toLocaleString('pt-BR')}
                        </p>
                    </div>
                    <div class="btn-group" role="group">
                        <button class="btn btn-sm btn-danger" onclick="removeFavorite('${fav.log_group_name}')" title="Remover dos favoritos">
                            <i class="bi bi-star-fill"></i>
                        </button>
                        <button class="btn btn-sm btn-primary" onclick="viewLogStreams('${fav.log_group_name}')" title="Ver Streams">
                            <i class="bi bi-file-text"></i> Streams
                        </button>
                        <button class="btn btn-sm btn-success" onclick="useInInsights('${fav.log_group_name}')" title="Usar no Insights">
                            <i class="bi bi-search"></i> Query
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
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
        fav.log_group_name.toLowerCase().includes(filter) ||
        (fav.alias && fav.alias.toLowerCase().includes(filter))
    );
    
    displayFavorites(filtered);
}

/**
 * Adiciona/Remove favorito (toggle sem confirmação)
 */
async function toggleFavorite(logGroupName) {
    // Remove qualquer encoding prévio
    logGroupName = decodeURIComponent(logGroupName);
    
    try {
        // Encode completo para usar na URL
        const encoded = encodeURIComponent(logGroupName);
        
        // Verifica se já é favorito
        const checkResponse = await fetch(`/cloudwatch/favorites/check/${encoded}`);
        const checkResult = await checkResponse.json();
        
        if (checkResult.is_favorite) {
            // Remove sem confirmação
            const response = await fetch(`/cloudwatch/favorites/${encoded}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.success) {
                showAlert(result.message, 'success');
                loadFavorites();
                loadLogGroups(); // Atualiza a lista principal
            } else {
                showAlert(result.message, 'danger');
            }
        } else {
            // Adiciona
            const response = await fetch('/cloudwatch/favorites', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    log_group_name: logGroupName
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                showAlert(result.message, 'success');
                loadFavorites();
                loadLogGroups(); // Atualiza a lista principal
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
async function removeFavorite(logGroupName) {
    // Remove qualquer encoding prévio
    logGroupName = decodeURIComponent(logGroupName);
    
    if (!confirm(`Remover "${logGroupName}" dos favoritos?`)) {
        return;
    }
    
    try {
        // Encode completo para preservar a barra inicial
        const encoded = encodeURIComponent(logGroupName);
        const response = await fetch(`/cloudwatch/favorites/${encoded}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            loadFavorites();
            loadLogGroups(); // Atualiza a lista principal também
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro: ${error.message}`, 'danger');
    }
}

// ==================== QUERIES SALVAS ====================

/**
 * Carrega queries salvas para o log group selecionado
 */
async function loadSavedQueriesForLogGroup() {
    const select = document.getElementById('insightsLogGroups');
    const selectedGroups = Array.from(select.selectedOptions).map(opt => opt.value);
    
    savedQueriesSelect.innerHTML = '<option value="">Selecione uma query salva...</option>';
    
    if (selectedGroups.length !== 1) {
        savedQueriesSelect.innerHTML = '<option value="">Selecione apenas 1 log group para ver queries salvas</option>';
        return;
    }
    
    const logGroupName = selectedGroups[0];
    
    try {
        // Encode cada parte do path separadamente
        const encodedLogGroup = logGroupName.split('/').map(part => encodeURIComponent(part)).join('/');
        const response = await fetch(`/cloudwatch/saved-queries/log-group/${encodedLogGroup}`);
        const result = await response.json();
        
        console.log('Queries carregadas:', result); // Debug
        
        if (result.success && result.queries && result.queries.length > 0) {
            result.queries.forEach(query => {
                const option = document.createElement('option');
                option.value = query.id;
                option.textContent = `${query.name}${query.description ? ' - ' + query.description : ''}`;
                option.dataset.queryString = query.query_string;
                savedQueriesSelect.appendChild(option);
            });
            showAlert(`${result.queries.length} query(ies) carregada(s)`, 'success');
        } else {
            savedQueriesSelect.innerHTML = '<option value="">Nenhuma query salva para este log group</option>';
        }
    } catch (error) {
        console.error('Erro ao carregar queries:', error);
        showAlert(`Erro ao carregar queries: ${error.message}`, 'danger');
    }
}

/**
 * Carrega query salva selecionada
 */
function loadSavedQuery() {
    const selectedOption = savedQueriesSelect.options[savedQueriesSelect.selectedIndex];
    
    if (selectedOption && selectedOption.dataset.queryString) {
        document.getElementById('insightsQuery').value = selectedOption.dataset.queryString;
        showAlert(`Query "${selectedOption.textContent}" carregada!`, 'success');
    }
}

/**
 * Salva query atual
 */
async function saveCurrentQuery() {
    const select = document.getElementById('insightsLogGroups');
    const selectedGroups = Array.from(select.selectedOptions).map(opt => opt.value);
    const queryString = document.getElementById('insightsQuery').value.trim();
    const queryName = document.getElementById('queryName').value.trim();
    const queryDescription = document.getElementById('queryDescription').value.trim();
    
    if (selectedGroups.length === 0) {
        showAlert('Selecione pelo menos um log group', 'warning');
        return;
    }
    
    if (!queryString) {
        showAlert('Digite uma query', 'warning');
        return;
    }
    
    if (!queryName) {
        showAlert('Digite um nome para a query', 'warning');
        return;
    }
    
    saveQueryBtn.disabled = true;
    saveQueryBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Salvando...';
    
    try {
        // Salva para cada log group selecionado
        for (const logGroupName of selectedGroups) {
            const response = await fetch('/cloudwatch/saved-queries', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: queryName,
                    log_group_name: logGroupName,
                    query_string: queryString,
                    description: queryDescription
                })
            });
            
            const result = await response.json();
            
            if (!result.success) {
                showAlert(`Erro ao salvar para ${logGroupName}: ${result.message}`, 'danger');
                return;
            }
        }
        
        showAlert(`Query "${queryName}" salva para ${selectedGroups.length} log group(s)!`, 'success');
        bootstrap.Modal.getInstance(document.getElementById('saveQueryModal')).hide();
        document.getElementById('queryName').value = '';
        document.getElementById('queryDescription').value = '';
        loadSavedQueriesForLogGroup();
        
    } catch (error) {
        showAlert(`Erro ao salvar query: ${error.message}`, 'danger');
    } finally {
        saveQueryBtn.disabled = false;
        saveQueryBtn.innerHTML = '<i class="bi bi-save"></i> Salvar';
    }
}
