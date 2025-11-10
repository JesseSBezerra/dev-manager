from flask import Blueprint, render_template, request, jsonify
from src.business.dynamodb_business import DynamoDBBusiness

# Cria o Blueprint para o controller de DynamoDB
dynamodb_bp = Blueprint('dynamodb', __name__, url_prefix='/dynamodb')

# Instancia a camada de negócio
business = DynamoDBBusiness()


@dynamodb_bp.route('/')
def index():
    """
    Renderiza a página principal para gerenciar tabelas DynamoDB
    """
    return render_template('dynamodb/index.html')


@dynamodb_bp.route('/create', methods=['POST'])
def create_table():
    """
    Endpoint para criar uma nova tabela DynamoDB
    
    Espera JSON com:
    - table_name: Nome da tabela
    - primary_key: Nome da chave primária
    - primary_key_type: Tipo da chave (S, N, ou B)
    """
    try:
        data = request.get_json()
        
        table_name = data.get('table_name', '').strip()
        primary_key = data.get('primary_key', '').strip()
        primary_key_type = data.get('primary_key_type', 'S').strip().upper()
        
        # Chama a camada de negócio para criar a tabela
        result = business.create_table(table_name, primary_key, primary_key_type)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao processar requisição: {str(e)}'
        }), 500


@dynamodb_bp.route('/list', methods=['GET'])
def list_tables():
    """
    Endpoint para listar todas as tabelas DynamoDB
    """
    try:
        result = business.list_tables()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar tabelas: {str(e)}'
        }), 500


@dynamodb_bp.route('/info/<table_name>', methods=['GET'])
def get_table_info(table_name):
    """
    Endpoint para obter informações de uma tabela específica
    
    Args:
        table_name: Nome da tabela
    """
    try:
        result = business.get_table_info(table_name)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter informações da tabela: {str(e)}'
        }), 500


@dynamodb_bp.route('/delete/<table_name>', methods=['DELETE'])
def delete_table(table_name):
    """
    Endpoint para deletar uma tabela DynamoDB
    
    Args:
        table_name: Nome da tabela
    """
    try:
        result = business.delete_table(table_name)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao deletar tabela: {str(e)}'
        }), 500
