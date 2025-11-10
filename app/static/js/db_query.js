// JavaScript para Database Query Tool

// Elementos do DOM
const alertContainer = document.getElementById('alertContainer');
const testConnectionBtn = document.getElementById('testConnectionBtn');
const loadTablesBtn = document.getElementById('loadTablesBtn');
const createTunnelBtn = document.getElementById('createTunnelBtn');
const savedTunnelsSelect = document.getElementById('savedTunnels');
const deleteTunnelBtn = document.getElementById('deleteTunnelBtn');
const confirmSaveTunnelBtn = document.getElementById('confirmSaveTunnelBtn');

// Variáveis globais
let currentTunnelData = {};
window.currentTunnelId = null;

// Event Listeners
testConnectionBtn.addEventListener('click', testConnection);
loadTablesBtn.addEventListener('click', loadTables);
createTunnelBtn.addEventListener('click', createTunnel);
document.getElementById('refreshBastionsBtn').addEventListener('click', loadBastions);
document.getElementById('refreshRdsBtn').addEventListener('click', loadRdsInstances);
savedTunnelsSelect.addEventListener('change', loadSavedTunnel);
deleteTunnelBtn.addEventListener('click', deleteSavedTunnel);
confirmSaveTunnelBtn.addEventListener('click', saveTunnel);

// Carregar túneis salvos ao iniciar
document.addEventListener('DOMContentLoaded', () => {
    loadSavedTunnels();
});

// Carregar listas quando o modal é aberto
document.getElementById('tunnelModal').addEventListener('show.bs.modal', () => {
    loadBastions();
    loadRdsInstances();
});

// Atualizar preview quando abrir modal de salvar
document.getElementById('saveTunnelModal').addEventListener('show.bs.modal', () => {
    updateSavePreview();
});

// Removido - agora é gerenciado pelo sistema de abas

// Auto-ajustar porta baseado no engine
document.getElementById('engine').addEventListener('change', (e) => {
    const portInput = document.getElementById('port');
    const rdsPortInput = document.getElementById('rdsPort');
    
    switch(e.target.value) {
        case 'mysql':
        case 'mariadb':
            portInput.value = 3306;
            if (rdsPortInput) rdsPortInput.value = 3306;
            break;
        case 'postgres':
            portInput.value = 5432;
            if (rdsPortInput) rdsPortInput.value = 5432;
            break;
    }
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
    
    alertContainer.innerHTML = '';
    alertContainer.appendChild(alertDiv);
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    setTimeout(() => {
        alertDiv.remove();
    }, 8000);
}

/**
 * Obtém dados do formulário de conexão
 */
function getConnectionData() {
    return {
        engine: document.getElementById('engine').value,
        host: document.getElementById('host').value,
        port: parseInt(document.getElementById('port').value),
        database: document.getElementById('database').value,
        username: document.getElementById('username').value,
        password: document.getElementById('password').value
    };
}

/**
 * Testa a conexão com o banco
 */
async function testConnection() {
    const data = getConnectionData();
    
    if (!data.engine || !data.database || !data.username || !data.password) {
        showAlert('Preencha todos os campos obrigatórios', 'warning');
        return;
    }
    
    testConnectionBtn.disabled = true;
    testConnectionBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Testando...';
    
    try {
        const response = await fetch('/db-query/test-connection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
        } else {
            showAlert(result.message, 'danger');
        }
        
    } catch (error) {
        showAlert(`Erro ao testar conexão: ${error.message}`, 'danger');
    } finally {
        testConnectionBtn.disabled = false;
        testConnectionBtn.innerHTML = '<i class="bi bi-check-circle"></i> Testar Conexão';
    }
}

/**
 * Carrega lista de tabelas
 */
async function loadTables() {
    const data = getConnectionData();
    
    if (!data.engine || !data.database || !data.username || !data.password) {
        showAlert('Preencha todos os campos obrigatórios', 'warning');
        return;
    }
    
    const modal = new bootstrap.Modal(document.getElementById('tablesModal'));
    const modalBody = document.getElementById('tablesModalBody');
    
    modalBody.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-info" role="status"></div>
            <p class="mt-2">Carregando tabelas...</p>
        </div>
    `;
    
    modal.show();
    
    try {
        const response = await fetch('/db-query/get-tables', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            if (result.tables.length === 0) {
                modalBody.innerHTML = `
                    <div class="alert alert-info">
                        Nenhuma tabela encontrada no banco de dados.
                    </div>
                `;
            } else {
                let html = `<p><strong>${result.count} tabela(s) encontrada(s):</strong></p><ul class="list-group">`;
                result.tables.forEach(table => {
                    html += `
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <span><i class="bi bi-table"></i> ${table}</span>
                            <button class="btn btn-sm btn-outline-primary" onclick="selectFromTable('${table}')">
                                SELECT *
                            </button>
                        </li>
                    `;
                });
                html += '</ul>';
                modalBody.innerHTML = html;
            }
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
                Erro ao carregar tabelas: ${error.message}
            </div>
        `;
    }
}

/**
 * Executa uma query SQL
 */
async function executeQuery() {
    const data = getConnectionData();
    const query = sqlQuery.value.trim();
    
    if (!query) {
        showAlert('Digite uma query SQL', 'warning');
        return;
    }
    
    if (!data.engine || !data.database || !data.username || !data.password) {
        showAlert('Preencha todos os campos de conexão', 'warning');
        return;
    }
    
    executeQueryBtn.disabled = true;
    executeQueryBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Executando...';
    
    resultsContainer.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2">Executando query...</p>
        </div>
    `;
    
    const startTime = Date.now();
    
    try {
        const response = await fetch('/db-query/execute-query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ...data,
                query: query
            })
        });
        
        const result = await response.json();
        const executionTime = Date.now() - startTime;
        
        if (result.success) {
            displayResults(result, executionTime);
            showAlert(`Query executada com sucesso em ${executionTime}ms`, 'success');
        } else {
            resultsContainer.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Erro:</strong> ${result.message}
                </div>
            `;
            showAlert(result.message, 'danger');
        }
        
    } catch (error) {
        resultsContainer.innerHTML = `
            <div class="alert alert-danger">
                Erro ao executar query: ${error.message}
            </div>
        `;
        showAlert(`Erro: ${error.message}`, 'danger');
    } finally {
        executeQueryBtn.disabled = false;
        executeQueryBtn.innerHTML = '<i class="bi bi-play-fill"></i> Executar Query';
    }
}

/**
 * Exibe os resultados da query
 */
function displayResults(result, executionTime) {
    if (result.type === 'select') {
        // Query SELECT - exibe tabela
        let html = `
            <div class="mb-3">
                <span class="badge bg-success">${result.row_count} linha(s)</span>
                <span class="badge bg-info">${executionTime}ms</span>
            </div>
        `;
        
        if (result.row_count === 0) {
            html += '<div class="alert alert-info">Nenhum resultado encontrado</div>';
        } else {
            html += '<div class="table-responsive"><table class="table table-striped table-hover table-sm">';
            
            // Cabeçalho
            html += '<thead class="table-dark"><tr>';
            result.columns.forEach(col => {
                html += `<th>${col}</th>`;
            });
            html += '</tr></thead>';
            
            // Linhas
            html += '<tbody>';
            result.rows.forEach(row => {
                html += '<tr>';
                result.columns.forEach(col => {
                    const value = row[col];
                    html += `<td>${value !== null && value !== undefined ? value : '<span class="text-muted">NULL</span>'}</td>`;
                });
                html += '</tr>';
            });
            html += '</tbody></table></div>';
        }
        
        resultsContainer.innerHTML = html;
        
    } else if (result.type === 'modify') {
        // Query INSERT/UPDATE/DELETE
        resultsContainer.innerHTML = `
            <div class="alert alert-success">
                <i class="bi bi-check-circle"></i> ${result.message}
                <br>
                <small>Tempo de execução: ${executionTime}ms</small>
            </div>
        `;
    }
}

/**
 * Limpa o editor de query
 */
function clearQuery() {
    sqlQuery.value = '';
    resultsContainer.innerHTML = `
        <div class="text-center text-muted">
            <i class="bi bi-inbox" style="font-size: 3rem;"></i>
            <p class="mt-2">Execute uma query para ver os resultados aqui</p>
        </div>
    `;
}

/**
 * Insere template de query
 */
function insertTemplate(type) {
    const templates = {
        'SELECT': 'SELECT * FROM tabela WHERE id = 1;',
        'INSERT': 'INSERT INTO tabela (coluna1, coluna2) VALUES (valor1, valor2);',
        'UPDATE': 'UPDATE tabela SET coluna1 = valor1 WHERE id = 1;',
        'DELETE': 'DELETE FROM tabela WHERE id = 1;'
    };
    
    sqlQuery.value = templates[type] || '';
    sqlQuery.focus();
}

/**
 * Insere SELECT * FROM tabela
 */
function selectFromTable(tableName) {
    sqlQuery.value = `SELECT * FROM ${tableName} LIMIT 100;`;
    bootstrap.Modal.getInstance(document.getElementById('tablesModal')).hide();
    sqlQuery.focus();
}

/**
 * Carrega lista de Bastions
 */
async function loadBastions() {
    const select = document.getElementById('bastionInstanceId');
    select.innerHTML = '<option value="">Carregando...</option>';
    
    try {
        const response = await fetch('/db-query/list-bastions');
        const result = await response.json();
        
        if (result.success) {
            if (result.bastions.length === 0) {
                select.innerHTML = '<option value="">Nenhum Bastion em execução</option>';
            } else {
                select.innerHTML = '<option value="">Selecione um Bastion...</option>';
                result.bastions.forEach(bastion => {
                    const option = document.createElement('option');
                    option.value = bastion.instance_id;
                    option.textContent = `${bastion.name} (${bastion.instance_id}) - ${bastion.private_ip}`;
                    select.appendChild(option);
                });
            }
        } else {
            select.innerHTML = '<option value="">Erro ao carregar</option>';
            showAlert(result.message, 'warning');
        }
    } catch (error) {
        select.innerHTML = '<option value="">Erro ao carregar</option>';
        console.error('Erro ao carregar Bastions:', error);
    }
}

/**
 * Carrega lista de instâncias RDS
 */
async function loadRdsInstances() {
    const select = document.getElementById('rdsEndpoint');
    select.innerHTML = '<option value="">Carregando...</option>';
    
    try {
        const response = await fetch('/db-query/list-rds');
        const result = await response.json();
        
        if (result.success) {
            if (result.rds_instances.length === 0) {
                select.innerHTML = '<option value="">Nenhuma instância RDS disponível</option>';
            } else {
                select.innerHTML = '<option value="">Selecione uma instância RDS...</option>';
                result.rds_instances.forEach(rds => {
                    const option = document.createElement('option');
                    option.value = rds.endpoint;
                    option.dataset.host = rds.endpoint;
                    option.dataset.port = rds.port;
                    option.dataset.engine = rds.engine;
                    option.textContent = `${rds.identifier} (${rds.engine}) - ${rds.endpoint}`;
                    select.appendChild(option);
                });
            }
        } else {
            select.innerHTML = '<option value="">Erro ao carregar</option>';
            showAlert(result.message, 'warning');
        }
    } catch (error) {
        select.innerHTML = '<option value="">Erro ao carregar</option>';
        console.error('Erro ao carregar RDS:', error);
    }
}

// Atualizar porta quando RDS é selecionado
document.getElementById('rdsEndpoint').addEventListener('change', (e) => {
    const selectedOption = e.target.options[e.target.selectedIndex];
    if (selectedOption.dataset.port) {
        document.getElementById('rdsPort').value = selectedOption.dataset.port;
        
        // Atualiza engine e porta na conexão principal
        const engine = selectedOption.dataset.engine;
        const engineSelect = document.getElementById('engine');
        if (engine === 'mysql') {
            engineSelect.value = 'mysql';
        } else if (engine === 'postgres') {
            engineSelect.value = 'postgres';
        } else if (engine === 'mariadb') {
            engineSelect.value = 'mariadb';
        }
    }
});

/**
 * Cria túnel SSM
 */
async function createTunnel() {
    const bastionId = document.getElementById('bastionInstanceId').value;
    const rdsEndpoint = document.getElementById('rdsEndpoint').value;
    const rdsPort = parseInt(document.getElementById('rdsPort').value);
    const localPort = document.getElementById('localPort').value;
    
    if (!bastionId || !rdsEndpoint || !rdsPort) {
        showAlert('Preencha todos os campos obrigatórios do túnel', 'warning');
        return;
    }
    
    createTunnelBtn.disabled = true;
    createTunnelBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Criando...';
    
    try {
        const response = await fetch('/db-query/create-tunnel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                bastion_instance_id: bastionId,
                rds_endpoint: rdsEndpoint,
                rds_port: rdsPort,
                local_port: localPort ? parseInt(localPort) : null
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(`${result.message} - Use localhost:${result.local_port} para conectar`, 'success');
            
            // Atualiza campos de conexão
            document.getElementById('host').value = 'localhost';
            document.getElementById('port').value = result.local_port;
            
            bootstrap.Modal.getInstance(document.getElementById('tunnelModal')).hide();
        } else {
            showAlert(result.message, 'danger');
        }
        
    } catch (error) {
        showAlert(`Erro ao criar túnel: ${error.message}`, 'danger');
    } finally {
        createTunnelBtn.disabled = false;
        createTunnelBtn.innerHTML = '<i class="bi bi-arrow-left-right"></i> Criar Túnel';
    }
}

// ==================== TÚNEIS SALVOS ====================

/**
 * Carrega lista de túneis salvos
 */
async function loadSavedTunnels() {
    try {
        const response = await fetch('/db-query/tunnels');
        const result = await response.json();
        
        if (result.success) {
            savedTunnelsSelect.innerHTML = '<option value="">Selecione um túnel salvo...</option>';
            
            result.tunnels.forEach(tunnel => {
                const option = document.createElement('option');
                option.value = tunnel.id;
                option.textContent = `${tunnel.name} (${tunnel.db_type} - ${tunnel.db_name})`;
                option.dataset.tunnel = JSON.stringify(tunnel);
                savedTunnelsSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erro ao carregar túneis:', error);
    }
}

/**
 * Carrega um túnel salvo
 */
async function loadSavedTunnel() {
    const selectedOption = savedTunnelsSelect.options[savedTunnelsSelect.selectedIndex];
    
    if (!selectedOption.value) {
        deleteTunnelBtn.disabled = true;
        window.currentTunnelId = null;
        return;
    }
    
    deleteTunnelBtn.disabled = false;
    
    const tunnel = JSON.parse(selectedOption.dataset.tunnel);
    window.currentTunnelId = tunnel.id;
    
    // Preenche os campos
    document.getElementById('engine').value = tunnel.db_type;
    document.getElementById('host').value = 'localhost';
    document.getElementById('port').value = tunnel.db_port;
    document.getElementById('database').value = tunnel.db_name;
    document.getElementById('username').value = tunnel.db_user;
    
    // Preenche senha se foi salva
    if (tunnel.db_password) {
        document.getElementById('password').value = tunnel.db_password;
    }
    
    // Salva dados do túnel
    currentTunnelData = {
        bastion_id: tunnel.bastion_id,
        db_host: tunnel.db_host,
        db_port: tunnel.db_port,
        db_name: tunnel.db_name,
        db_user: tunnel.db_user,
        db_type: tunnel.db_type
    };
    
    showAlert(`Túnel "${tunnel.name}" carregado! Criando túnel SSM...`, 'info');
    
    // Cria o túnel SSM automaticamente
    await createTunnelForSaved(tunnel);
    
    // Carrega comandos salvos para todas as abas
    if (typeof loadSavedCommandsForTab === 'function') {
        tabs.forEach(tab => loadSavedCommandsForTab(tab.id));
    }
}

/**
 * Cria túnel SSM para túnel salvo
 */
async function createTunnelForSaved(tunnel) {
    try {
        const response = await fetch('/db-query/create-tunnel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                bastion_instance_id: tunnel.bastion_id,
                rds_endpoint: tunnel.db_host,
                rds_port: tunnel.db_port,
                local_port: null
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(`${result.message} - Conectado em localhost:${result.local_port}`, 'success');
            
            // Atualiza porta local
            document.getElementById('port').value = result.local_port;
            
            // Testa conexão automaticamente se tiver senha
            if (tunnel.db_password) {
                setTimeout(() => testConnection(), 1000);
            }
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro ao criar túnel: ${error.message}`, 'danger');
    }
}

/**
 * Deleta um túnel salvo
 */
async function deleteSavedTunnel() {
    const tunnelId = savedTunnelsSelect.value;
    
    if (!tunnelId) {
        return;
    }
    
    const tunnelName = savedTunnelsSelect.options[savedTunnelsSelect.selectedIndex].textContent;
    
    if (!confirm(`Tem certeza que deseja deletar o túnel "${tunnelName}"?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/db-query/tunnels/${tunnelId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            savedTunnelsSelect.value = '';
            deleteTunnelBtn.disabled = true;
            loadSavedTunnels();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro ao deletar túnel: ${error.message}`, 'danger');
    }
}

/**
 * Atualiza preview do túnel a ser salvo
 */
function updateSavePreview() {
    // Pega o select do bastion e extrai o ID
    const bastionSelect = document.getElementById('bastionInstanceId');
    const bastionId = bastionSelect.value || '-';
    
    // Pega o select do RDS e extrai o host
    const rdsSelect = document.getElementById('rdsEndpoint');
    const rdsOption = rdsSelect.options[rdsSelect.selectedIndex];
    const rdsHost = rdsOption ? rdsOption.dataset.host || rdsOption.value : '-';
    
    document.getElementById('previewBastionId').textContent = bastionId;
    document.getElementById('previewDbHost').textContent = rdsHost;
    document.getElementById('previewDbPort').textContent = 
        document.getElementById('rdsPort').value || '-';
    document.getElementById('previewDbName').textContent = 
        document.getElementById('database').value || '-';
    document.getElementById('previewDbUser').textContent = 
        document.getElementById('username').value || '-';
    document.getElementById('previewDbType').textContent = 
        document.getElementById('engine').value || '-';
}

/**
 * Salva um túnel
 */
async function saveTunnel() {
    const name = document.getElementById('tunnelName').value.trim();
    const description = document.getElementById('tunnelDescription').value.trim();
    const savePassword = document.getElementById('savePasswordCheck').checked;
    
    // Pega o bastion ID
    const bastionSelect = document.getElementById('bastionInstanceId');
    const bastionId = bastionSelect.value;
    
    // Pega o RDS host
    const rdsSelect = document.getElementById('rdsEndpoint');
    const rdsOption = rdsSelect.options[rdsSelect.selectedIndex];
    const dbHost = rdsOption ? rdsOption.dataset.host || rdsOption.value : '';
    
    const dbPort = document.getElementById('rdsPort').value;
    const dbName = document.getElementById('database').value;
    const dbUser = document.getElementById('username').value;
    const dbPassword = savePassword ? document.getElementById('password').value : null;
    const dbType = document.getElementById('engine').value;
    
    if (!name) {
        showAlert('Nome do túnel é obrigatório', 'warning');
        return;
    }
    
    if (!bastionId || !dbHost || !dbPort || !dbName || !dbUser || !dbType) {
        showAlert('Preencha todos os campos de conexão antes de salvar', 'warning');
        return;
    }
    
    confirmSaveTunnelBtn.disabled = true;
    confirmSaveTunnelBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Salvando...';
    
    try {
        const response = await fetch('/db-query/tunnels', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name,
                description,
                bastion_id: bastionId,
                db_host: dbHost,
                db_port: parseInt(dbPort),
                db_name: dbName,
                db_user: dbUser,
                db_password: dbPassword,
                db_type: dbType
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            bootstrap.Modal.getInstance(document.getElementById('saveTunnelModal')).hide();
            document.getElementById('tunnelName').value = '';
            document.getElementById('tunnelDescription').value = '';
            loadSavedTunnels();
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro ao salvar túnel: ${error.message}`, 'danger');
    } finally {
        confirmSaveTunnelBtn.disabled = false;
        confirmSaveTunnelBtn.innerHTML = '<i class="bi bi-bookmark-plus"></i> Salvar';
    }
}
