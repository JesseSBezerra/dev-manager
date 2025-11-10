// JavaScript para gerenciar tabelas DynamoDB

// Elementos do DOM
const createTableForm = document.getElementById('createTableForm');
const createBtn = document.getElementById('createBtn');
const refreshBtn = document.getElementById('refreshBtn');
const tablesContainer = document.getElementById('tablesContainer');
const alertContainer = document.getElementById('alertContainer');

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    loadTables();
});

createTableForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    await createTable();
});

refreshBtn.addEventListener('click', () => {
    loadTables();
});

/**
 * Exibe um alerta na página
 */
function showAlert(message, type = 'info', errors = []) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    
    let errorList = '';
    if (errors && errors.length > 0) {
        errorList = '<ul class="mb-0 mt-2">';
        errors.forEach(error => {
            errorList += `<li>${error}</li>`;
        });
        errorList += '</ul>';
    }
    
    alertDiv.innerHTML = `
        <strong>${type === 'success' ? 'Sucesso!' : type === 'danger' ? 'Erro!' : 'Atenção!'}</strong> ${message}
        ${errorList}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.innerHTML = '';
    alertContainer.appendChild(alertDiv);
    
    // Remove o alerta após 5 segundos
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

/**
 * Cria uma nova tabela DynamoDB
 */
async function createTable() {
    const formData = new FormData(createTableForm);
    const data = {
        table_name: formData.get('table_name'),
        primary_key: formData.get('primary_key'),
        primary_key_type: formData.get('primary_key_type')
    };
    
    // Desabilita o botão durante a requisição
    createBtn.disabled = true;
    createBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Criando...';
    
    try {
        const response = await fetch('/dynamodb/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            createTableForm.reset();
            loadTables(); // Recarrega a lista de tabelas
        } else {
            showAlert(result.message, 'danger', result.errors);
        }
        
    } catch (error) {
        showAlert('Erro ao conectar com o servidor: ' + error.message, 'danger');
    } finally {
        // Reabilita o botão
        createBtn.disabled = false;
        createBtn.innerHTML = '<i class="bi bi-plus-lg"></i> Criar Tabela';
    }
}

/**
 * Carrega a lista de tabelas existentes
 */
async function loadTables() {
    tablesContainer.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
            <p class="mt-2">Carregando tabelas...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/dynamodb/list');
        const result = await response.json();
        
        if (result.success) {
            displayTables(result.tables);
        } else {
            tablesContainer.innerHTML = `
                <div class="alert alert-warning">
                    <i class="bi bi-exclamation-triangle"></i> ${result.message}
                </div>
            `;
        }
        
    } catch (error) {
        tablesContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-x-circle"></i> Erro ao carregar tabelas: ${error.message}
            </div>
        `;
    }
}

/**
 * Exibe a lista de tabelas na interface
 */
function displayTables(tables) {
    if (!tables || tables.length === 0) {
        tablesContainer.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-inbox"></i>
                <h5>Nenhuma tabela encontrada</h5>
                <p class="text-muted">Crie sua primeira tabela DynamoDB usando o formulário acima.</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="row">';
    
    tables.forEach(tableName => {
        html += `
            <div class="col-md-6 mb-3">
                <div class="table-item">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <div class="table-name">
                                <i class="bi bi-table"></i> ${tableName}
                            </div>
                            <div class="table-status">
                                <span class="badge bg-success">Ativa</span>
                            </div>
                        </div>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-info" onclick="viewTableInfo('${tableName}')" title="Ver detalhes">
                                <i class="bi bi-info-circle"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="confirmDeleteTable('${tableName}')" title="Deletar">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    tablesContainer.innerHTML = html;
}

/**
 * Visualiza informações detalhadas de uma tabela
 */
async function viewTableInfo(tableName) {
    try {
        const response = await fetch(`/dynamodb/info/${tableName}`);
        const result = await response.json();
        
        if (result.success) {
            const tableData = result.data;
            const keySchema = tableData.KeySchema[0];
            const attributeDef = tableData.AttributeDefinitions[0];
            
            const info = `
                <strong>Nome:</strong> ${tableData.TableName}<br>
                <strong>Status:</strong> ${tableData.TableStatus}<br>
                <strong>Chave Primária:</strong> ${keySchema.AttributeName} (${attributeDef.AttributeType})<br>
                <strong>Itens:</strong> ${tableData.ItemCount || 0}<br>
                <strong>Tamanho:</strong> ${(tableData.TableSizeBytes / 1024).toFixed(2)} KB<br>
                <strong>Criada em:</strong> ${new Date(tableData.CreationDateTime).toLocaleString('pt-BR')}
            `;
            
            showAlert(info, 'info');
        } else {
            showAlert(result.message, 'danger');
        }
        
    } catch (error) {
        showAlert('Erro ao obter informações: ' + error.message, 'danger');
    }
}

/**
 * Confirma a exclusão de uma tabela
 */
function confirmDeleteTable(tableName) {
    if (confirm(`Tem certeza que deseja deletar a tabela "${tableName}"?\n\nEsta ação não pode ser desfeita!`)) {
        deleteTable(tableName);
    }
}

/**
 * Deleta uma tabela DynamoDB
 */
async function deleteTable(tableName) {
    try {
        const response = await fetch(`/dynamodb/delete/${tableName}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            loadTables(); // Recarrega a lista
        } else {
            showAlert(result.message, 'danger');
        }
        
    } catch (error) {
        showAlert('Erro ao deletar tabela: ' + error.message, 'danger');
    }
}
