// JavaScript para gerenciar EC2 Instances

// Elementos do DOM
const instancesContainer = document.getElementById('instancesContainer');
const alertContainer = document.getElementById('alertContainer');
const createBastionBtn = document.getElementById('createBastionBtn');
const createInstanceBtn = document.getElementById('createInstanceBtn');
const refreshInstancesBtn = document.getElementById('refreshInstancesBtn');

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    loadInstances();
});

refreshInstancesBtn.addEventListener('click', () => {
    loadInstances();
});

createBastionBtn.addEventListener('click', () => {
    createBastionHost();
});

createInstanceBtn.addEventListener('click', () => {
    createInstance();
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
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    setTimeout(() => {
        alertDiv.remove();
    }, 8000);
}

/**
 * Carrega a lista de instâncias EC2
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
        const response = await fetch('/ec2/instances');
        const result = await response.json();
        
        if (result.success) {
            displayInstances(result.instances);
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
 * Exibe a lista de instâncias
 */
function displayInstances(instances) {
    if (!instances || instances.length === 0) {
        instancesContainer.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-inbox"></i>
                <h5>Nenhuma instância encontrada</h5>
                <p class="text-muted">Crie sua primeira instância EC2 ou Bastion Host.</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="table-responsive"><table class="table table-hover">';
    html += `
        <thead>
            <tr>
                <th>Nome</th>
                <th>ID</th>
                <th>Tipo</th>
                <th>Estado</th>
                <th>Tipo Instância</th>
                <th>IP Público</th>
                <th>IP Privado</th>
                <th>Ações</th>
            </tr>
        </thead>
        <tbody>
    `;
    
    instances.forEach(instance => {
        const stateColor = getStateColor(instance.state);
        const isRunning = instance.state === 'running';
        const isStopped = instance.state === 'stopped';
        const isBastion = instance.type_tag === 'Bastion';
        
        html += `
            <tr>
                <td>
                    <strong>${instance.name}</strong>
                    ${isBastion ? '<br><span class="badge bg-success">Bastion</span>' : ''}
                </td>
                <td><code>${instance.instance_id}</code></td>
                <td>${instance.instance_type}</td>
                <td><span class="badge bg-${stateColor}">${instance.state}</span></td>
                <td>${instance.instance_type}</td>
                <td>${instance.public_ip !== 'N/A' ? `<code>${instance.public_ip}</code>` : '<span class="text-muted">-</span>'}</td>
                <td>${instance.private_ip !== 'N/A' ? `<code>${instance.private_ip}</code>` : '<span class="text-muted">-</span>'}</td>
                <td>
                    <div class="btn-group btn-group-sm" role="group">
                        ${isRunning ? `
                            ${isBastion ? `
                                <button class="btn btn-outline-success" onclick="showSSMConnection('${instance.instance_id}')" title="Conectar via SSM">
                                    <i class="bi bi-terminal"></i>
                                </button>
                            ` : ''}
                            <button class="btn btn-outline-warning" onclick="confirmStopInstance('${instance.instance_id}')" title="Parar">
                                <i class="bi bi-stop-circle"></i>
                            </button>
                        ` : ''}
                        ${isStopped ? `
                            <button class="btn btn-outline-success" onclick="confirmStartInstance('${instance.instance_id}')" title="Iniciar">
                                <i class="bi bi-play-circle"></i>
                            </button>
                        ` : ''}
                        <button class="btn btn-outline-info" onclick="viewInstanceDetails('${instance.instance_id}')" title="Detalhes">
                            <i class="bi bi-info-circle"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="confirmTerminateInstance('${instance.instance_id}')" title="Terminar">
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
 * Retorna a cor do badge baseado no estado
 */
function getStateColor(state) {
    const colors = {
        'running': 'success',
        'stopped': 'secondary',
        'pending': 'info',
        'stopping': 'warning',
        'shutting-down': 'warning',
        'terminated': 'danger',
        'terminating': 'danger'
    };
    return colors[state] || 'secondary';
}

/**
 * Cria um Bastion Host
 */
async function createBastionHost() {
    const form = document.getElementById('createBastionForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const data = {
        name: document.getElementById('bastionName').value,
        instance_type: document.getElementById('bastionInstanceType').value,
        key_name: document.getElementById('bastionKeyName').value || null,
        subnet_id: document.getElementById('bastionSubnetId').value || null
    };
    
    createBastionBtn.disabled = true;
    createBastionBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Criando...';
    
    try {
        const response = await fetch('/ec2/instances/bastion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message + ' - A instância levará alguns minutos para ficar disponível.', 'success');
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('createBastionModal'));
            modal.hide();
            
            form.reset();
            setTimeout(() => loadInstances(), 2000);
        } else {
            showAlert(result.message, 'danger');
        }
        
    } catch (error) {
        showAlert(`Erro ao criar Bastion Host: ${error.message}`, 'danger');
    } finally {
        createBastionBtn.disabled = false;
        createBastionBtn.innerHTML = '<i class="bi bi-shield-check"></i> Criar Bastion Host';
    }
}

/**
 * Cria uma instância EC2 genérica
 */
async function createInstance() {
    const form = document.getElementById('createInstanceForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const data = {
        name: document.getElementById('instanceName').value,
        ami_id: document.getElementById('instanceAmiId').value,
        instance_type: document.getElementById('instanceType').value,
        key_name: document.getElementById('instanceKeyName').value || null
    };
    
    createInstanceBtn.disabled = true;
    createInstanceBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Criando...';
    
    try {
        const response = await fetch('/ec2/instances', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('createInstanceModal'));
            modal.hide();
            
            form.reset();
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
 * Confirma e inicia uma instância
 */
function confirmStartInstance(instanceId) {
    if (confirm(`Deseja INICIAR a instância ${instanceId}?`)) {
        startInstance(instanceId);
    }
}

/**
 * Inicia uma instância
 */
async function startInstance(instanceId) {
    try {
        showAlert(`Iniciando instância ${instanceId}...`, 'info');
        
        const response = await fetch(`/ec2/instances/${instanceId}/start`, {
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
 * Confirma e para uma instância
 */
function confirmStopInstance(instanceId) {
    if (confirm(`Deseja PARAR a instância ${instanceId}?`)) {
        stopInstance(instanceId);
    }
}

/**
 * Para uma instância
 */
async function stopInstance(instanceId) {
    try {
        showAlert(`Parando instância ${instanceId}...`, 'info');
        
        const response = await fetch(`/ec2/instances/${instanceId}/stop`, {
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
 * Confirma e termina uma instância
 */
function confirmTerminateInstance(instanceId) {
    if (confirm(`ATENÇÃO: Deseja TERMINAR (deletar) a instância ${instanceId}?\n\nEsta ação é IRREVERSÍVEL!`)) {
        terminateInstance(instanceId);
    }
}

/**
 * Termina uma instância
 */
async function terminateInstance(instanceId) {
    try {
        showAlert(`Terminando instância ${instanceId}...`, 'info');
        
        const response = await fetch(`/ec2/instances/${instanceId}/terminate`, {
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
        showAlert(`Erro ao terminar instância: ${error.message}`, 'danger');
    }
}

/**
 * Mostra informações de conexão SSM
 */
async function showSSMConnection(instanceId) {
    const modal = new bootstrap.Modal(document.getElementById('ssmConnectionModal'));
    const modalBody = document.getElementById('ssmConnectionBody');
    
    modalBody.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-success" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
        </div>
    `;
    
    modal.show();
    
    try {
        const response = await fetch(`/ec2/instances/${instanceId}/ssm-connection`);
        const result = await response.json();
        
        if (result.success) {
            modalBody.innerHTML = `
                <h6>Comando de Conexão SSM:</h6>
                <div class="alert alert-dark">
                    <code>${result.command}</code>
                    <button class="btn btn-sm btn-outline-light float-end" onclick="copyToClipboard('${result.command}')">
                        <i class="bi bi-clipboard"></i> Copiar
                    </button>
                </div>
                
                <h6 class="mt-4">Túnel para RDS (Port Forwarding):</h6>
                <div class="alert alert-dark">
                    <code>aws ssm start-session --target ${instanceId} --document-name AWS-StartPortForwardingSessionToRemoteHost --parameters host="SEU-RDS-ENDPOINT",portNumber="3306",localPortNumber="3306"</code>
                    <button class="btn btn-sm btn-outline-light float-end" onclick="copyTunnelCommand('${instanceId}')">
                        <i class="bi bi-clipboard"></i> Copiar
                    </button>
                </div>
                
                <h6 class="mt-4">Instruções:</h6>
                <ol>
                    ${result.instructions.map(inst => `<li>${inst}</li>`).join('')}
                </ol>
                
                <div class="alert alert-info mt-3">
                    <strong>Dica:</strong> Substitua "SEU-RDS-ENDPOINT" pelo endpoint real do seu RDS.
                    Após criar o túnel, conecte-se localmente em <code>localhost:3306</code>
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
                Erro ao obter informações: ${error.message}
            </div>
        `;
    }
}

/**
 * Visualiza detalhes de uma instância
 */
async function viewInstanceDetails(instanceId) {
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
        const response = await fetch(`/ec2/instances/${instanceId}`);
        const result = await response.json();
        
        if (result.success) {
            const instance = result.instance;
            
            modalBody.innerHTML = `
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <strong>Nome:</strong><br>${instance.name}
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>ID:</strong><br><code>${instance.instance_id}</code>
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>Estado:</strong><br>
                        <span class="badge bg-${getStateColor(instance.state)}">${instance.state}</span>
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>Tipo:</strong><br>${instance.instance_type}
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>AMI ID:</strong><br><code>${instance.ami_id}</code>
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>Key Pair:</strong><br>${instance.key_name}
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>IP Público:</strong><br>${instance.public_ip}
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>IP Privado:</strong><br>${instance.private_ip}
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>VPC ID:</strong><br>${instance.vpc_id}
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>Subnet ID:</strong><br>${instance.subnet_id}
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>Availability Zone:</strong><br>${instance.availability_zone}
                    </div>
                    <div class="col-md-6 mb-3">
                        <strong>Security Groups:</strong><br>${instance.security_groups.join(', ') || 'N/A'}
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
        showAlert('Comando copiado para a área de transferência!', 'success');
    }).catch(err => {
        showAlert('Erro ao copiar: ' + err, 'danger');
    });
}

/**
 * Copia comando de túnel para clipboard
 */
function copyTunnelCommand(instanceId) {
    const command = `aws ssm start-session --target ${instanceId} --document-name AWS-StartPortForwardingSessionToRemoteHost --parameters host="SEU-RDS-ENDPOINT",portNumber="3306",localPortNumber="3306"`;
    copyToClipboard(command);
}
