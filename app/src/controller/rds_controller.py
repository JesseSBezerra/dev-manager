from flask import Blueprint, render_template, request, jsonify
from src.business.rds_business import RDSBusiness
from src.database.db_manager import DatabaseManager

# Cria o Blueprint para o controller de RDS
rds_bp = Blueprint('rds', __name__, url_prefix='/rds')

# Instancia a camada de negócio
business = RDSBusiness()
db = DatabaseManager()


@rds_bp.route('/')
def index():
    """
    Renderiza a página principal para gerenciar instâncias RDS
    """
    return render_template('rds/index.html')


@rds_bp.route('/instances', methods=['GET'])
def list_instances():
    """
    Endpoint para listar todas as instâncias RDS
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


@rds_bp.route('/instances/<db_instance_identifier>', methods=['GET'])
def get_instance(db_instance_identifier):
    """
    Endpoint para obter detalhes de uma instância RDS
    
    Args:
        db_instance_identifier: Identificador da instância
    """
    try:
        result = business.get_instance_details(db_instance_identifier)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter detalhes da instância: {str(e)}'
        }), 500


@rds_bp.route('/instances', methods=['POST'])
def create_instance():
    """
    Endpoint para criar uma nova instância RDS
    
    Body JSON:
        db_instance_identifier: Identificador único
        db_instance_class: Classe da instância (ex: db.t3.micro)
        engine: Engine do banco (mysql, postgres, etc)
        master_username: Usuário master
        master_password: Senha master
        allocated_storage: Storage em GB (opcional, padrão: 20)
        db_name: Nome do banco inicial (opcional)
        publicly_accessible: Acesso público (opcional, padrão: false)
        multi_az: Multi-AZ (opcional, padrão: false)
    """
    try:
        data = request.get_json()
        
        result = business.create_instance(
            db_instance_identifier=data.get('db_instance_identifier'),
            db_instance_class=data.get('db_instance_class'),
            engine=data.get('engine'),
            master_username=data.get('master_username'),
            master_password=data.get('master_password'),
            allocated_storage=int(data.get('allocated_storage', 20)),
            db_name=data.get('db_name'),
            publicly_accessible=data.get('publicly_accessible', False),
            multi_az=data.get('multi_az', False)
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


@rds_bp.route('/instances/<db_instance_identifier>', methods=['DELETE'])
def delete_instance(db_instance_identifier):
    """
    Endpoint para deletar uma instância RDS
    
    Args:
        db_instance_identifier: Identificador da instância
    
    Query params:
        skip_final_snapshot: true/false (padrão: false)
    """
    try:
        skip_snapshot = request.args.get('skip_final_snapshot', 'false').lower() == 'true'
        
        result = business.delete_instance(
            db_instance_identifier=db_instance_identifier,
            skip_final_snapshot=skip_snapshot
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao deletar instância: {str(e)}'
        }), 500


@rds_bp.route('/instances/<db_instance_identifier>/stop', methods=['POST'])
def stop_instance(db_instance_identifier):
    """
    Endpoint para parar uma instância RDS
    
    Args:
        db_instance_identifier: Identificador da instância
    """
    try:
        result = business.stop_instance(db_instance_identifier)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao parar instância: {str(e)}'
        }), 500


@rds_bp.route('/instances/<db_instance_identifier>/start', methods=['POST'])
def start_instance(db_instance_identifier):
    """
    Endpoint para iniciar uma instância RDS
    
    Args:
        db_instance_identifier: Identificador da instância
    """
    try:
        result = business.start_instance(db_instance_identifier)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao iniciar instância: {str(e)}'
        }), 500


# ==================== FAVORITOS ====================

@rds_bp.route('/favorites', methods=['GET'])
def get_favorites():
    """
    Obtém lista de instâncias favoritas
    """
    try:
        result = db.get_favorite_rds_instances()
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500


@rds_bp.route('/favorites/<instance_identifier>', methods=['POST'])
def add_favorite(instance_identifier):
    """
    Adiciona instância aos favoritos
    """
    try:
        data = request.get_json() or {}
        alias = data.get('alias')
        result = db.add_favorite_rds_instance(instance_identifier, alias)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500


@rds_bp.route('/favorites/<instance_identifier>', methods=['DELETE'])
def remove_favorite(instance_identifier):
    """
    Remove instância dos favoritos
    """
    try:
        result = db.remove_favorite_rds_instance(instance_identifier)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500


@rds_bp.route('/favorites/<instance_identifier>/check', methods=['GET'])
def check_favorite(instance_identifier):
    """
    Verifica se instância está nos favoritos
    """
    try:
        is_favorite = db.is_favorite_rds_instance(instance_identifier)
        return jsonify({
            'success': True,
            'is_favorite': is_favorite
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500
