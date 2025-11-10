from flask import Blueprint, render_template, request, jsonify
from src.business.ecs_business import ECSBusiness
from src.database.db_manager import DatabaseManager

# Cria o Blueprint para o controller de ECS
ecs_bp = Blueprint('ecs', __name__, url_prefix='/ecs')

# Instancia a camada de negócio
business = ECSBusiness()
db = DatabaseManager()


@ecs_bp.route('/')
def index():
    """
    Renderiza a página principal para visualizar clusters e serviços ECS
    """
    return render_template('ecs/index.html')


@ecs_bp.route('/clusters', methods=['GET'])
def list_clusters():
    """
    Endpoint para listar todos os clusters ECS
    """
    try:
        result = business.list_all_clusters()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar clusters: {str(e)}'
        }), 500


@ecs_bp.route('/clusters/<cluster_name>/services', methods=['GET'])
def list_services(cluster_name):
    """
    Endpoint para listar todos os serviços de um cluster
    
    Args:
        cluster_name: Nome do cluster
    """
    try:
        result = business.list_cluster_services(cluster_name)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar serviços: {str(e)}'
        }), 500


@ecs_bp.route('/clusters/<cluster_name>/tasks', methods=['GET'])
def list_tasks(cluster_name):
    """
    Endpoint para listar todas as tasks de um cluster
    
    Args:
        cluster_name: Nome do cluster
    
    Query params:
        service_name: (opcional) Nome do serviço para filtrar tasks
    """
    try:
        service_name = request.args.get('service_name', None)
        result = business.list_cluster_tasks(cluster_name, service_name)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar tasks: {str(e)}'
        }), 500


@ecs_bp.route('/clusters/<cluster_name>/info', methods=['GET'])
def get_cluster_info(cluster_name):
    """
    Endpoint para obter informações detalhadas de um cluster
    
    Args:
        cluster_name: Nome do cluster
    """
    try:
        result = business.get_cluster_info(cluster_name)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter informações do cluster: {str(e)}'
        }), 500


@ecs_bp.route('/clusters/<cluster_name>/services/<service_name>/info', methods=['GET'])
def get_service_info(cluster_name, service_name):
    """
    Endpoint para obter informações detalhadas de um serviço
    
    Args:
        cluster_name: Nome do cluster
        service_name: Nome do serviço
    """
    try:
        result = business.get_service_info(cluster_name, service_name)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter informações do serviço: {str(e)}'
        }), 500


@ecs_bp.route('/clusters/<cluster_name>/services/<service_name>/stop', methods=['POST'])
def stop_service(cluster_name, service_name):
    """
    Endpoint para parar um serviço ECS (desiredCount = 0)
    
    Args:
        cluster_name: Nome do cluster
        service_name: Nome do serviço
    """
    try:
        result = business.stop_service(cluster_name, service_name)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao parar serviço: {str(e)}'
        }), 500


@ecs_bp.route('/clusters/<cluster_name>/services/<service_name>/start', methods=['POST'])
def start_service(cluster_name, service_name):
    """
    Endpoint para iniciar um serviço ECS
    
    Args:
        cluster_name: Nome do cluster
        service_name: Nome do serviço
    
    Body JSON:
        desired_count: Número desejado de tasks
    """
    try:
        data = request.get_json()
        desired_count = data.get('desired_count', 1)
        
        result = business.start_service(cluster_name, service_name, desired_count)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao iniciar serviço: {str(e)}'
        }), 500


@ecs_bp.route('/clusters/<cluster_name>/services/<service_name>/change-capacity', methods=['POST'])
def change_capacity_provider(cluster_name, service_name):
    """
    Endpoint para alterar o Capacity Provider de um serviço
    
    Args:
        cluster_name: Nome do cluster
        service_name: Nome do serviço
    
    Body JSON:
        capacity_provider: FARGATE ou FARGATE_SPOT
    """
    try:
        data = request.get_json()
        capacity_provider = data.get('capacity_provider', '').upper()
        
        result = business.change_capacity_provider(cluster_name, service_name, capacity_provider)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao alterar capacity provider: {str(e)}'
        }), 500


# ==================== FAVORITOS ====================

@ecs_bp.route('/favorites', methods=['GET'])
def get_favorites():
    """
    Obtém lista de clusters favoritos
    """
    try:
        result = db.get_favorite_ecs_clusters()
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500


@ecs_bp.route('/favorites/<cluster_name>', methods=['POST'])
def add_favorite(cluster_name):
    """
    Adiciona cluster aos favoritos
    """
    try:
        data = request.get_json() or {}
        alias = data.get('alias')
        result = db.add_favorite_ecs_cluster(cluster_name, alias)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500


@ecs_bp.route('/favorites/<cluster_name>', methods=['DELETE'])
def remove_favorite(cluster_name):
    """
    Remove cluster dos favoritos
    """
    try:
        result = db.remove_favorite_ecs_cluster(cluster_name)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500


@ecs_bp.route('/favorites/<cluster_name>/check', methods=['GET'])
def check_favorite(cluster_name):
    """
    Verifica se cluster está nos favoritos
    """
    try:
        is_favorite = db.is_favorite_ecs_cluster(cluster_name)
        return jsonify({
            'success': True,
            'is_favorite': is_favorite
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500
