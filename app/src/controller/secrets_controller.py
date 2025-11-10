from flask import Blueprint, render_template, request, jsonify
from src.business.secrets_business import SecretsManagerBusiness
from src.database.db_manager import DatabaseManager

# Cria o Blueprint para o controller de Secrets Manager
secrets_bp = Blueprint('secrets', __name__, url_prefix='/secrets')

# Instancia a camada de negócio e banco de dados
business = SecretsManagerBusiness()
db_manager = DatabaseManager()


@secrets_bp.route('/')
def index():
    """
    Renderiza a página principal do Secrets Manager
    """
    return render_template('secrets/index.html')


@secrets_bp.route('/list', methods=['GET'])
def list_secrets():
    """
    Lista todos os segredos
    """
    try:
        result = business.list_all_secrets()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar segredos: {str(e)}'
        }), 500


@secrets_bp.route('/<secret_name>', methods=['GET'])
def describe_secret(secret_name):
    """
    Obtém detalhes de um segredo (sem revelar o valor)
    
    Args:
        secret_name: Nome do segredo
    """
    try:
        result = business.describe_secret(secret_name)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter detalhes: {str(e)}'
        }), 500


@secrets_bp.route('/<secret_name>/value', methods=['GET'])
def get_secret_value(secret_name):
    """
    Obtém o valor de um segredo
    
    Args:
        secret_name: Nome do segredo
    """
    try:
        result = business.get_secret_value(secret_name)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter valor: {str(e)}'
        }), 500


@secrets_bp.route('/create', methods=['POST'])
def create_secret():
    """
    Cria um novo segredo
    
    Body JSON:
        name: Nome do segredo
        secret_value: Valor do segredo
        description: Descrição (opcional)
        tags: Lista de tags (opcional)
    """
    try:
        data = request.get_json()
        
        result = business.create_secret(
            name=data.get('name'),
            secret_value=data.get('secret_value'),
            description=data.get('description'),
            tags=data.get('tags')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao criar segredo: {str(e)}'
        }), 500


@secrets_bp.route('/<secret_name>/update', methods=['PUT'])
def update_secret(secret_name):
    """
    Atualiza o valor de um segredo
    
    Args:
        secret_name: Nome do segredo
    
    Body JSON:
        secret_value: Novo valor
    """
    try:
        data = request.get_json()
        
        result = business.update_secret(
            secret_name=secret_name,
            secret_value=data.get('secret_value')
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar segredo: {str(e)}'
        }), 500


@secrets_bp.route('/<secret_name>/delete', methods=['DELETE'])
def delete_secret(secret_name):
    """
    Deleta um segredo
    
    Args:
        secret_name: Nome do segredo
    
    Query params:
        recovery_days: Dias para recuperação (7-30, padrão 30)
        force: true para deletar imediatamente
    """
    try:
        recovery_days = int(request.args.get('recovery_days', 30))
        force_delete = request.args.get('force', 'false').lower() == 'true'
        
        result = business.delete_secret(
            secret_name=secret_name,
            recovery_window_days=recovery_days,
            force_delete=force_delete
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao deletar segredo: {str(e)}'
        }), 500


@secrets_bp.route('/<secret_name>/restore', methods=['POST'])
def restore_secret(secret_name):
    """
    Restaura um segredo deletado
    
    Args:
        secret_name: Nome do segredo
    """
    try:
        result = business.restore_secret(secret_name)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao restaurar segredo: {str(e)}'
        }), 500


# ==================== FAVORITOS ====================

@secrets_bp.route('/favorites', methods=['GET'])
def get_favorites():
    """
    Lista todos os secrets favoritos
    """
    try:
        result = db_manager.get_favorite_secrets()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar favoritos: {str(e)}'
        }), 500


@secrets_bp.route('/favorites', methods=['POST'])
def add_favorite():
    """
    Adiciona secret aos favoritos
    
    Body JSON:
        secret_name: Nome do secret
        alias: Apelido (opcional)
    """
    try:
        data = request.get_json()
        
        result = db_manager.add_favorite_secret(
            secret_name=data.get('secret_name'),
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


@secrets_bp.route('/favorites/<secret_name>', methods=['DELETE'])
def remove_favorite(secret_name):
    """
    Remove secret dos favoritos
    
    Args:
        secret_name: Nome do secret
    """
    try:
        result = db_manager.remove_favorite_secret(secret_name)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao remover favorito: {str(e)}'
        }), 500


@secrets_bp.route('/favorites/check/<secret_name>', methods=['GET'])
def check_favorite(secret_name):
    """
    Verifica se um secret é favorito
    
    Args:
        secret_name: Nome do secret
    """
    try:
        is_fav = db_manager.is_favorite_secret(secret_name)
        
        return jsonify({
            'success': True,
            'is_favorite': is_fav
        }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao verificar favorito: {str(e)}'
        }), 500
