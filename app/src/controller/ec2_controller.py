from flask import Blueprint, render_template, request, jsonify
from src.business.ec2_business import EC2Business

# Cria o Blueprint para o controller de EC2
ec2_bp = Blueprint('ec2', __name__, url_prefix='/ec2')

# Instancia a camada de negócio
business = EC2Business()


@ec2_bp.route('/')
def index():
    """
    Renderiza a página principal para gerenciar instâncias EC2
    """
    return render_template('ec2/index.html')


@ec2_bp.route('/instances', methods=['GET'])
def list_instances():
    """
    Endpoint para listar todas as instâncias EC2
    """
    try:
        result = business.list_all_instances()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar instâncias: {str(e)}'
        }), 500


@ec2_bp.route('/instances/<instance_id>', methods=['GET'])
def get_instance(instance_id):
    """
    Endpoint para obter detalhes de uma instância EC2
    
    Args:
        instance_id: ID da instância
    """
    try:
        result = business.get_instance_details(instance_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter detalhes: {str(e)}'
        }), 500


@ec2_bp.route('/instances/bastion', methods=['POST'])
def create_bastion():
    """
    Endpoint para criar um Bastion Host com SSM
    
    Body JSON:
        name: Nome da instância
        instance_type: Tipo da instância (opcional, padrão: t3.micro)
        key_name: Nome do key pair (opcional)
        subnet_id: ID da subnet (opcional)
        security_group_ids: Lista de IDs de security groups (opcional)
    """
    try:
        data = request.get_json()
        
        result = business.create_bastion_host(
            name=data.get('name'),
            instance_type=data.get('instance_type', 't3.micro'),
            key_name=data.get('key_name'),
            subnet_id=data.get('subnet_id'),
            security_group_ids=data.get('security_group_ids')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao criar Bastion Host: {str(e)}'
        }), 500


@ec2_bp.route('/instances', methods=['POST'])
def create_instance():
    """
    Endpoint para criar uma instância EC2 genérica
    
    Body JSON:
        name: Nome da instância
        ami_id: ID da AMI
        instance_type: Tipo da instância
        key_name: Nome do key pair (opcional)
        subnet_id: ID da subnet (opcional)
        security_group_ids: Lista de IDs de security groups (opcional)
        user_data: Script de inicialização (opcional)
    """
    try:
        data = request.get_json()
        
        result = business.create_instance(
            name=data.get('name'),
            ami_id=data.get('ami_id'),
            instance_type=data.get('instance_type'),
            key_name=data.get('key_name'),
            subnet_id=data.get('subnet_id'),
            security_group_ids=data.get('security_group_ids'),
            user_data=data.get('user_data')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao criar instância: {str(e)}'
        }), 500


@ec2_bp.route('/instances/<instance_id>/start', methods=['POST'])
def start_instance(instance_id):
    """
    Endpoint para iniciar uma instância EC2
    
    Args:
        instance_id: ID da instância
    """
    try:
        result = business.start_instance(instance_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao iniciar instância: {str(e)}'
        }), 500


@ec2_bp.route('/instances/<instance_id>/stop', methods=['POST'])
def stop_instance(instance_id):
    """
    Endpoint para parar uma instância EC2
    
    Args:
        instance_id: ID da instância
    """
    try:
        result = business.stop_instance(instance_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao parar instância: {str(e)}'
        }), 500


@ec2_bp.route('/instances/<instance_id>/terminate', methods=['DELETE'])
def terminate_instance(instance_id):
    """
    Endpoint para terminar (deletar) uma instância EC2
    
    Args:
        instance_id: ID da instância
    """
    try:
        result = business.terminate_instance(instance_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao terminar instância: {str(e)}'
        }), 500


@ec2_bp.route('/instances/<instance_id>/ssm-connection', methods=['GET'])
def get_ssm_connection(instance_id):
    """
    Endpoint para obter comando de conexão SSM
    
    Args:
        instance_id: ID da instância
    """
    try:
        result = business.get_ssm_connection_info(instance_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter informações SSM: {str(e)}'
        }), 500


@ec2_bp.route('/amis', methods=['GET'])
def list_amis():
    """
    Endpoint para listar AMIs disponíveis
    """
    try:
        result = business.list_available_amis()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar AMIs: {str(e)}'
        }), 500
