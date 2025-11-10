// Sistema de Abas para SQL Editor
// Este arquivo complementa o db_query.js com funcionalidades de abas

// Variáveis do sistema de abas
var tabs = [];
var activeTabId = null;
var tabCounter = 0;

// Inicializar sistema de abas
document.addEventListener('DOMContentLoaded', () => {
    createNewTab();
    document.getElementById('newTabBtn').addEventListener('click', createNewTab);
    
    // Atualizar checkbox de salvar senha
    document.getElementById('savePasswordCheck').addEventListener('change', updatePasswordPreview);
});

/**
 * Cria uma nova aba
 */
function createNewTab() {
    tabCounter++;
    const tabId = `tab-${tabCounter}`;
    
    const tab = {
        id: tabId,
        name: `Query ${tabCounter}`,
        sql: '',
        results: null
    };
    
    tabs.push(tab);
    renderTabs();
    switchToTab(tabId);
}

/**
 * Renderiza todas as abas
 */
function renderTabs() {
    const tabsContainer = document.getElementById('sqlTabs');
    const contentContainer = document.getElementById('sqlTabsContent');
    
    tabsContainer.innerHTML = '';
    contentContainer.innerHTML = '';
    
    tabs.forEach((tab, index) => {
        // Criar aba
        const li = document.createElement('li');
        li.className = 'nav-item';
        li.innerHTML = `
            <a class="nav-link ${tab.id === activeTabId ? 'active' : ''}" 
               id="${tab.id}-tab" 
               data-bs-toggle="tab" 
               href="#${tab.id}" 
               role="tab">
                ${tab.name}
                ${tabs.length > 1 ? `<button class="btn-close btn-close-sm ms-2" onclick="closeTab('${tab.id}', event)" style="font-size: 0.7rem;"></button>` : ''}
            </a>
        `;
        tabsContainer.appendChild(li);
        
        // Criar conteúdo
        const div = document.createElement('div');
        div.className = `tab-pane fade ${tab.id === activeTabId ? 'show active' : ''}`;
        div.id = tab.id;
        div.role = 'tabpanel';
        div.innerHTML = `
            <div class="row mb-3">
                <div class="col-md-8">
                    <select class="form-select form-select-sm" id="${tab.id}-savedCommands" onchange="loadSavedCommand('${tab.id}')">
                        <option value="">Comandos salvos...</option>
                    </select>
                </div>
                <div class="col-md-4 text-end">
                    <button class="btn btn-sm btn-outline-primary" onclick="openSaveCommandModal('${tab.id}')">
                        <i class="bi bi-save"></i> Salvar Comando
                    </button>
                </div>
            </div>
            
            <div class="mb-3">
                <textarea class="form-control font-monospace" id="${tab.id}-sql" rows="8" 
                          placeholder="SELECT * FROM tabela WHERE ...">${tab.sql}</textarea>
                <small class="text-muted">Dica: Use Ctrl+Enter para executar</small>
            </div>
            
            <div class="d-flex gap-2 mb-3">
                <button type="button" class="btn btn-primary" onclick="executeQueryTab('${tab.id}')">
                    <i class="bi bi-play-fill"></i> Executar
                </button>
                <button type="button" class="btn btn-secondary" onclick="clearQueryTab('${tab.id}')">
                    <i class="bi bi-x-circle"></i> Limpar
                </button>
                
                <div class="btn-group" role="group">
                    <button type="button" class="btn btn-outline-secondary btn-sm" onclick="insertTemplateTab('${tab.id}', 'SELECT')">
                        SELECT
                    </button>
                    <button type="button" class="btn btn-outline-secondary btn-sm" onclick="insertTemplateTab('${tab.id}', 'INSERT')">
                        INSERT
                    </button>
                    <button type="button" class="btn btn-outline-secondary btn-sm" onclick="insertTemplateTab('${tab.id}', 'UPDATE')">
                        UPDATE
                    </button>
                    <button type="button" class="btn btn-outline-secondary btn-sm" onclick="insertTemplateTab('${tab.id}', 'DELETE')">
                        DELETE
                    </button>
                </div>
            </div>
            
            <div id="${tab.id}-info" class="alert alert-info d-none">
                <i class="bi bi-info-circle"></i> <span id="${tab.id}-infoText"></span>
            </div>
            
            <div id="${tab.id}-results">
                ${tab.results || '<div class="text-center text-muted"><i class="bi bi-inbox" style="font-size: 2rem;"></i><p class="mt-2">Execute uma query para ver os resultados</p></div>'}
            </div>
        `;
        contentContainer.appendChild(div);
        
        // Adicionar event listener para Ctrl+Enter
        const textarea = div.querySelector(`#${tab.id}-sql`);
        textarea.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                executeQueryTab(tab.id);
            }
        });
    });
    
    // Carregar comandos salvos para a aba ativa
    if (activeTabId && window.currentTunnelId) {
        loadSavedCommandsForTab(activeTabId);
    }
}

/**
 * Troca para uma aba
 */
function switchToTab(tabId) {
    activeTabId = tabId;
    renderTabs();
}

/**
 * Fecha uma aba
 */
function closeTab(tabId, event) {
    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }
    
    if (tabs.length === 1) {
        showAlert('Você precisa ter pelo menos uma aba aberta', 'warning');
        return;
    }
    
    const index = tabs.findIndex(t => t.id === tabId);
    if (index !== -1) {
        tabs.splice(index, 1);
        
        // Se fechou a aba ativa, ativa a anterior ou próxima
        if (tabId === activeTabId) {
            const newIndex = Math.max(0, index - 1);
            activeTabId = tabs[newIndex].id;
        }
        
        renderTabs();
    }
}

/**
 * Executa query na aba
 */
async function executeQueryTab(tabId) {
    const textarea = document.getElementById(`${tabId}-sql`);
    const sql = textarea.value.trim();
    
    if (!sql) {
        showAlert('Digite uma query SQL', 'warning');
        return;
    }
    
    const resultsDiv = document.getElementById(`${tabId}-results`);
    resultsDiv.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2">Executando query...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/db-query/execute-query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                engine: document.getElementById('engine').value,
                host: document.getElementById('host').value,
                port: parseInt(document.getElementById('port').value),
                database: document.getElementById('database').value,
                username: document.getElementById('username').value,
                password: document.getElementById('password').value,
                query: sql
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayQueryResults(tabId, result);
            
            // Atualiza o resultado na aba
            const tab = tabs.find(t => t.id === tabId);
            if (tab) {
                tab.results = resultsDiv.innerHTML;
            }
        } else {
            resultsDiv.innerHTML = `<div class="alert alert-danger">${result.message}</div>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<div class="alert alert-danger">Erro: ${error.message}</div>`;
    }
}

/**
 * Exibe resultados da query
 */
function displayQueryResults(tabId, result) {
    const resultsDiv = document.getElementById(`${tabId}-results`);
    const infoDiv = document.getElementById(`${tabId}-info`);
    const infoText = document.getElementById(`${tabId}-infoText`);
    
    if (result.rows && result.rows.length > 0) {
        infoDiv.classList.remove('d-none');
        infoText.textContent = `${result.rows.length} linha(s) retornada(s) em ${result.execution_time}s`;
        
        let html = '<div class="table-responsive"><table class="table table-sm table-striped table-hover">';
        html += '<thead class="table-dark"><tr>';
        
        result.columns.forEach(col => {
            html += `<th>${col}</th>`;
        });
        html += '</tr></thead><tbody>';
        
        result.rows.forEach(row => {
            html += '<tr>';
            result.columns.forEach(col => {
                const value = row[col];
                html += `<td>${value !== null && value !== undefined ? value : '<span class="text-muted">NULL</span>'}</td>`;
            });
            html += '</tr>';
        });
        
        html += '</tbody></table></div>';
        resultsDiv.innerHTML = html;
    } else {
        infoDiv.classList.remove('d-none');
        infoText.textContent = `Query executada com sucesso em ${result.execution_time}s. ${result.affected_rows || 0} linha(s) afetada(s).`;
        resultsDiv.innerHTML = '<div class="alert alert-success">Query executada com sucesso!</div>';
    }
}

/**
 * Limpa query da aba
 */
function clearQueryTab(tabId) {
    document.getElementById(`${tabId}-sql`).value = '';
    document.getElementById(`${tabId}-results`).innerHTML = `
        <div class="text-center text-muted">
            <i class="bi bi-inbox" style="font-size: 2rem;"></i>
            <p class="mt-2">Execute uma query para ver os resultados</p>
        </div>
    `;
    document.getElementById(`${tabId}-info`).classList.add('d-none');
}

/**
 * Insere template SQL na aba
 */
function insertTemplateTab(tabId, type) {
    const textarea = document.getElementById(`${tabId}-sql`);
    const templates = {
        'SELECT': 'SELECT * FROM tabela WHERE condicao;',
        'INSERT': 'INSERT INTO tabela (coluna1, coluna2) VALUES (valor1, valor2);',
        'UPDATE': 'UPDATE tabela SET coluna1 = valor1 WHERE condicao;',
        'DELETE': 'DELETE FROM tabela WHERE condicao;'
    };
    
    textarea.value = templates[type] || '';
    textarea.focus();
}

/**
 * Carrega comandos salvos para a aba
 */
async function loadSavedCommandsForTab(tabId) {
    try {
        const url = window.currentTunnelId 
            ? `/db-query/sql-commands?tunnel_id=${window.currentTunnelId}`
            : '/db-query/sql-commands';
            
        const response = await fetch(url);
        const result = await response.json();
        
        if (result.success) {
            const select = document.getElementById(`${tabId}-savedCommands`);
            if (select) {
                select.innerHTML = '<option value="">Comandos salvos...</option>';
                result.commands.forEach(cmd => {
                    const option = document.createElement('option');
                    option.value = cmd.id;
                    option.textContent = cmd.name;
                    option.dataset.sql = cmd.sql_command;
                    select.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('Erro ao carregar comandos:', error);
    }
}

/**
 * Carrega um comando salvo na aba
 */
function loadSavedCommand(tabId) {
    const select = document.getElementById(`${tabId}-savedCommands`);
    const selectedOption = select.options[select.selectedIndex];
    
    if (selectedOption.value) {
        const sql = selectedOption.dataset.sql;
        document.getElementById(`${tabId}-sql`).value = sql;
        showAlert(`Comando "${selectedOption.textContent}" carregado!`, 'success');
    }
}

/**
 * Abre modal para salvar comando
 */
function openSaveCommandModal(tabId) {
    const sql = document.getElementById(`${tabId}-sql`).value.trim();
    
    if (!sql) {
        showAlert('Digite um comando SQL antes de salvar', 'warning');
        return;
    }
    
    const name = prompt('Nome do comando:');
    if (!name) return;
    
    const description = prompt('Descrição (opcional):');
    
    saveCommand(tabId, name, sql, description);
}

/**
 * Salva um comando SQL
 */
async function saveCommand(tabId, name, sql, description) {
    try {
        const response = await fetch('/db-query/sql-commands', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tunnel_id: window.currentTunnelId,
                name,
                sql_command: sql,
                description
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            loadSavedCommandsForTab(tabId);
        } else {
            showAlert(result.message, 'danger');
        }
    } catch (error) {
        showAlert(`Erro ao salvar comando: ${error.message}`, 'danger');
    }
}

/**
 * Atualiza preview da senha
 */
function updatePasswordPreview() {
    const checkbox = document.getElementById('savePasswordCheck');
    const preview = document.getElementById('previewPassword');
    
    if (checkbox.checked) {
        preview.textContent = 'Será salva';
        preview.className = 'text-warning fw-bold';
    } else {
        preview.textContent = 'Não será salva';
        preview.className = '';
    }
}
