from flask import Blueprint, render_template, request, jsonify
from urllib.parse import unquote
from src.business.parameter_store_business import ParameterStoreBusiness
from src.database.db_manager import DatabaseManager

# Cria o Blueprint para o controller de Parameter Store
parameters_bp = Blueprint('parameters', __name__, url_prefix='/parameters')

# Instancia a camada de negócio e banco de dados
business = ParameterStoreBusiness()
db_manager = DatabaseManager()


@parameters_bp.route('/')
def index():
    """
    Renderiza a página principal do Parameter Store
    """
    return render_template('parameters/index.html')


@parameters_bp.route('/list', methods=['GET'])
def list_parameters():
    """
    Lista todos os parâmetros
    """
    try:
        result = business.list_all_parameters()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar parâmetros: {str(e)}'
        }), 500


@parameters_bp.route('/<path:parameter_name>', methods=['GET'])
def get_parameter_details(parameter_name):
    """
    Obtém detalhes de um parâmetro
    
    Args:
        parameter_name: Nome do parâmetro
    """
    try:
        parameter_name = unquote(parameter_name)
        if not parameter_name.startswith('/'):
            parameter_name = '/' + parameter_name
            
        result = business.get_parameter_details(parameter_name)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter detalhes: {str(e)}'
        }), 500


@parameters_bp.route('/<path:parameter_name>/value', methods=['GET'])
def get_parameter_value(parameter_name):
    """
    Obtém o valor de um parâmetro
    
    Args:
        parameter_name: Nome do parâmetro
    """
    try:
        parameter_name = unquote(parameter_name)
        # Garante que começa com /
        if not parameter_name.startswith('/'):
            parameter_name = '/' + parameter_name
            
        result = business.get_parameter_value(parameter_name)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter valor: {str(e)}'
        }), 500


@parameters_bp.route('/<path:parameter_name>/history', methods=['GET'])
def get_parameter_history(parameter_name):
    """
    Obtém histórico de um parâmetro
    
    Args:
        parameter_name: Nome do parâmetro
    """
    try:
        parameter_name = unquote(parameter_name)
        if not parameter_name.startswith('/'):
            parameter_name = '/' + parameter_name
            
        result = business.get_history(parameter_name)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter histórico: {str(e)}'
        }), 500


@parameters_bp.route('/create', methods=['POST'])
def create_parameter():
    """
    Cria um novo parâmetro
    
    Body JSON:
        name: Nome do parâmetro
        value: Valor
        type: Tipo (String, StringList, SecureString)
        description: Descrição (opcional)
    """
    try:
        data = request.get_json()
        
        result = business.create_new_parameter(
            name=data.get('name'),
            value=data.get('value'),
            parameter_type=data.get('type', 'String'),
            description=data.get('description')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao criar parâmetro: {str(e)}'
        }), 500


@parameters_bp.route('/<path:parameter_name>/update', methods=['PUT'])
def update_parameter(parameter_name):
    """
    Atualiza um parâmetro
    
    Args:
        parameter_name: Nome do parâmetro
    
    Body JSON:
        value: Novo valor
        description: Nova descrição (opcional)
    """
    try:
        parameter_name = unquote(parameter_name)
        if not parameter_name.startswith('/'):
            parameter_name = '/' + parameter_name
            
        data = request.get_json()
        
        result = business.update_existing_parameter(
            name=parameter_name,
            value=data.get('value'),
            description=data.get('description')
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar parâmetro: {str(e)}'
        }), 500


@parameters_bp.route('/<path:parameter_name>', methods=['DELETE'])
def delete_parameter(parameter_name):
    """
    Deleta um parâmetro
    
    Args:
        parameter_name: Nome do parâmetro
    """
    try:
        parameter_name = unquote(parameter_name)
        if not parameter_name.startswith('/'):
            parameter_name = '/' + parameter_name
            
        result = business.delete_parameter(parameter_name)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao deletar parâmetro: {str(e)}'
        }), 500


@parameters_bp.route('/by-path', methods=['POST'])
def get_by_path():
    """
    Obtém parâmetros por caminho
    
    Body JSON:
        path: Caminho (ex: /app/prod/)
    """
    try:
        data = request.get_json()
        result = business.get_by_path(data.get('path'))
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar por caminho: {str(e)}'
        }), 500


# ==================== FAVORITOS ====================

@parameters_bp.route('/favorites', methods=['GET'])
def get_favorites():
    """
    Lista todos os parameters favoritos
    """
    try:
        result = db_manager.get_favorite_parameters()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar favoritos: {str(e)}'
        }), 500


@parameters_bp.route('/favorites', methods=['POST'])
def add_favorite():
    """
    Adiciona parameter aos favoritos
    
    Body JSON:
        parameter_name: Nome do parameter
        alias: Apelido (opcional)
    """
    try:
        data = request.get_json()
        
        result = db_manager.add_favorite_parameter(
            parameter_name=data.get('parameter_name'),
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


@parameters_bp.route('/favorites/<path:parameter_name>', methods=['DELETE'])
def remove_favorite(parameter_name):
    """
    Remove parameter dos favoritos
    
    Args:
        parameter_name: Nome do parameter
    """
    try:
        parameter_name = unquote(parameter_name)
        if not parameter_name.startswith('/'):
            parameter_name = '/' + parameter_name
            
        result = db_manager.remove_favorite_parameter(parameter_name)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao remover favorito: {str(e)}'
        }), 500


@parameters_bp.route('/favorites/check/<path:parameter_name>', methods=['GET'])
def check_favorite(parameter_name):
    """
    Verifica se um parameter é favorito
    
    Args:
        parameter_name: Nome do parameter
    """
    try:
        parameter_name = unquote(parameter_name)
        if not parameter_name.startswith('/'):
            parameter_name = '/' + parameter_name
            
        is_fav = db_manager.is_favorite_parameter(parameter_name)
        
        return jsonify({
            'success': True,
            'is_favorite': is_fav
        }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao verificar favorito: {str(e)}'
        }), 500
