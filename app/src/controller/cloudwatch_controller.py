from flask import Blueprint, render_template, request, jsonify
from src.business.cloudwatch_business import CloudWatchLogsBusiness
from src.database.db_manager import DatabaseManager
from urllib.parse import unquote

# Cria o Blueprint para o controller de CloudWatch Logs
cloudwatch_bp = Blueprint('cloudwatch', __name__, url_prefix='/cloudwatch')

# Instancia a camada de negócio e banco de dados
business = CloudWatchLogsBusiness()
db_manager = DatabaseManager()


@cloudwatch_bp.route('/')
def index():
    """
    Renderiza a página principal do CloudWatch Logs
    """
    return render_template('cloudwatch/index.html')


@cloudwatch_bp.route('/log-groups', methods=['GET'])
def list_log_groups():
    """
    Lista todos os log groups
    
    Query params:
        prefix: Prefixo para filtrar (opcional)
    """
    try:
        prefix = request.args.get('prefix')
        result = business.list_all_log_groups(prefix)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar log groups: {str(e)}'
        }), 500


@cloudwatch_bp.route('/log-groups/<path:log_group_name>', methods=['GET'])
def get_log_group_details(log_group_name):
    """
    Obtém detalhes de um log group
    
    Args:
        log_group_name: Nome do log group
    """
    try:
        # Decodifica o nome do log group
        log_group_name = unquote(log_group_name)
        result = business.get_log_group_details(log_group_name)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter detalhes: {str(e)}'
        }), 500


@cloudwatch_bp.route('/log-groups/<path:log_group_name>/streams', methods=['GET'])
def list_log_streams(log_group_name):
    """
    Lista log streams de um log group
    
    Args:
        log_group_name: Nome do log group
    
    Query params:
        limit: Número máximo de streams (padrão 50)
    """
    try:
        # Decodifica o nome do log group
        log_group_name = unquote(log_group_name)
        limit = int(request.args.get('limit', 50))
        result = business.list_streams(log_group_name, limit)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar streams: {str(e)}'
        }), 500


@cloudwatch_bp.route('/log-groups/<path:log_group_name>/streams/<path:log_stream_name>/events', methods=['GET'])
def get_log_events(log_group_name, log_stream_name):
    """
    Obtém eventos de um log stream
    
    Args:
        log_group_name: Nome do log group
        log_stream_name: Nome do log stream
    
    Query params:
        limit: Número máximo de eventos (padrão 100)
        hours_ago: Horas atrás para buscar (padrão 24)
    """
    try:
        # Decodifica os nomes
        log_group_name = unquote(log_group_name)
        log_stream_name = unquote(log_stream_name)
        
        limit = int(request.args.get('limit', 100))
        hours_ago = int(request.args.get('hours_ago', 24))
        
        result = business.get_events(log_group_name, log_stream_name, limit, hours_ago)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter eventos: {str(e)}'
        }), 500


@cloudwatch_bp.route('/log-groups/<path:log_group_name>/filter', methods=['POST'])
def filter_log_events(log_group_name):
    """
    Filtra eventos de log
    
    Args:
        log_group_name: Nome do log group
    
    Body JSON:
        filter_pattern: Padrão de filtro (opcional)
        hours_ago: Horas atrás (padrão 24)
        limit: Limite de eventos (padrão 100)
    """
    try:
        # Decodifica o nome do log group
        log_group_name = unquote(log_group_name)
        data = request.get_json()
        
        result = business.filter_events(
            log_group_name=log_group_name,
            filter_pattern=data.get('filter_pattern'),
            hours_ago=int(data.get('hours_ago', 24)),
            limit=int(data.get('limit', 100))
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao filtrar eventos: {str(e)}'
        }), 500


@cloudwatch_bp.route('/insights/query', methods=['POST'])
def execute_insights_query():
    """
    Executa uma query no CloudWatch Logs Insights
    
    Body JSON:
        log_group_names: Lista de log groups ou string única
        query_string: Query em CloudWatch Insights syntax
        hours_ago: Horas atrás (padrão 24)
        limit: Limite de resultados (padrão 1000)
    """
    try:
        data = request.get_json()
        
        result = business.execute_insights_query(
            log_group_names=data.get('log_group_names'),
            query_string=data.get('query_string'),
            hours_ago=int(data.get('hours_ago', 24)),
            limit=int(data.get('limit', 1000))
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao executar query: {str(e)}'
        }), 500


# ==================== QUERIES SALVAS ====================

@cloudwatch_bp.route('/saved-queries', methods=['GET'])
def get_all_saved_queries():
    """
    Lista todas as queries salvas
    """
    try:
        result = db_manager.get_all_queries()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar queries: {str(e)}'
        }), 500


@cloudwatch_bp.route('/saved-queries/log-group/<path:log_group_name>', methods=['GET'])
def get_queries_by_log_group(log_group_name):
    """
    Lista queries de um log group específico
    
    Args:
        log_group_name: Nome do log group
    """
    try:
        log_group_name = unquote(log_group_name)
        result = db_manager.get_queries_by_log_group(log_group_name)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar queries: {str(e)}'
        }), 500


@cloudwatch_bp.route('/saved-queries', methods=['POST'])
def save_query():
    """
    Salva uma nova query
    
    Body JSON:
        name: Nome da query
        log_group_name: Nome do log group
        query_string: Query SQL
        description: Descrição (opcional)
    """
    try:
        data = request.get_json()
        
        result = db_manager.save_query(
            name=data.get('name'),
            log_group_name=data.get('log_group_name'),
            query_string=data.get('query_string'),
            description=data.get('description')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao salvar query: {str(e)}'
        }), 500


@cloudwatch_bp.route('/saved-queries/<int:query_id>', methods=['GET'])
def get_query_by_id(query_id):
    """
    Obtém uma query específica
    
    Args:
        query_id: ID da query
    """
    try:
        result = db_manager.get_query_by_id(query_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar query: {str(e)}'
        }), 500


@cloudwatch_bp.route('/saved-queries/<int:query_id>', methods=['DELETE'])
def delete_query(query_id):
    """
    Deleta uma query
    
    Args:
        query_id: ID da query
    """
    try:
        result = db_manager.delete_query(query_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao deletar query: {str(e)}'
        }), 500


# ==================== FAVORITOS ====================

@cloudwatch_bp.route('/favorites', methods=['GET'])
def get_favorites():
    """
    Lista todos os log groups favoritos
    """
    try:
        result = db_manager.get_favorites()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar favoritos: {str(e)}'
        }), 500


@cloudwatch_bp.route('/favorites', methods=['POST'])
def add_favorite():
    """
    Adiciona log group aos favoritos
    
    Body JSON:
        log_group_name: Nome do log group
        alias: Apelido (opcional)
    """
    try:
        data = request.get_json()
        
        result = db_manager.add_favorite(
            log_group_name=data.get('log_group_name'),
            alias=data.get('alias')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao adicionar favorito: {str(e)}'
        }), 500


@cloudwatch_bp.route('/favorites/<path:log_group_name>', methods=['DELETE'])
def remove_favorite(log_group_name):
    """
    Remove log group dos favoritos
    
    Args:
        log_group_name: Nome do log group
    """
    try:
        log_group_name = unquote(log_group_name)
        log_group_name = '/'+log_group_name
        result = db_manager.remove_favorite(log_group_name)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao remover favorito: {str(e)}'
        }), 500


@cloudwatch_bp.route('/favorites/check/<path:log_group_name>', methods=['GET'])
def check_favorite(log_group_name):
    """
    Verifica se um log group é favorito
    
    Args:
        log_group_name: Nome do log group
    """
    try:
        log_group_name = unquote(log_group_name)
        is_fav = db_manager.is_favorite(log_group_name)
        
        return jsonify({
            'success': True,
            'is_favorite': is_fav
        }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao verificar favorito: {str(e)}'
        }), 500
