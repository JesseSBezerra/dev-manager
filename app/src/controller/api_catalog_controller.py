from flask import Blueprint, render_template, request, jsonify
from src.service.api_catalog_service import APICatalogService

# Cria o Blueprint
api_catalog_bp = Blueprint('api_catalog', __name__, url_prefix='/api-catalog')

# Instancia o service
service = APICatalogService()


@api_catalog_bp.route('/')
def index():
    """
    Página principal do catálogo de APIs
    """
    return render_template('api_catalog/index.html')


# ==================== OWNERS ====================

@api_catalog_bp.route('/owners', methods=['GET'])
def get_owners():
    """
    Lista todos os donos
    """
    try:
        result = service.get_owners()
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500


@api_catalog_bp.route('/owners', methods=['POST'])
def create_owner():
    """
    Cria um novo dono
    """
    try:
        data = request.get_json()
        result = service.create_owner(
            name=data.get('name'),
            description=data.get('description')
        )
        return jsonify(result), 201 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500


# ==================== APIS ====================

@api_catalog_bp.route('/apis', methods=['GET'])
def get_apis():
    """
    Lista APIs
    """
    try:
        owner_id = request.args.get('owner_id')
        result = service.get_apis(owner_id=owner_id)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500


@api_catalog_bp.route('/apis', methods=['POST'])
def create_api():
    """
    Cria uma nova API
    """
    try:
        data = request.get_json()
        result = service.create_api(
            name=data.get('name'),
            owner_id=data.get('owner_id'),
            base_url=data.get('base_url'),
            description=data.get('description')
        )
        return jsonify(result), 201 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500


@api_catalog_bp.route('/apis/<api_id>', methods=['GET'])
def get_api(api_id):
    """
    Obtém detalhes de uma API
    """
    try:
        result = service.get_api(api_id)
        return jsonify(result), 200 if result['success'] else 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500


@api_catalog_bp.route('/apis/<api_id>', methods=['DELETE'])
def delete_api(api_id):
    """
    Deleta uma API
    """
    try:
        result = service.delete_api(api_id)
        return jsonify(result), 200 if result['success'] else 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500


# ==================== AUTHENTICATIONS ====================

@api_catalog_bp.route('/authentications', methods=['GET'])
def get_authentications():
    """
    Lista autenticações
    """
    try:
        owner_id = request.args.get('owner_id')
        result = service.get_authentications(owner_id=owner_id)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500


@api_catalog_bp.route('/authentications', methods=['POST'])
def create_authentication():
    """
    Cria uma autenticação
    """
    try:
        data = request.get_json()
        result = service.create_authentication(
            owner_id=data.get('owner_id'),
            name=data.get('name'),
            auth_type=data.get('auth_type'),
            auth_config=data.get('auth_config', {}),
            token_field=data.get('token_field')
        )
        return jsonify(result), 201 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500


# ==================== ENDPOINTS ====================

@api_catalog_bp.route('/endpoints', methods=['GET'])
def get_endpoints():
    """
    Lista endpoints de uma API
    """
    try:
        api_id = request.args.get('api_id')
        if not api_id:
            return jsonify({
                'success': False,
                'message': 'api_id é obrigatório'
            }), 400
        
        result = service.get_endpoints(api_id)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500


@api_catalog_bp.route('/endpoints', methods=['POST'])
def create_endpoint():
    """
    Cria um endpoint
    """
    try:
        data = request.get_json()
        result = service.create_endpoint(
            api_id=data.get('api_id'),
            path=data.get('path'),
            description=data.get('description')
        )
        return jsonify(result), 201 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500


# ==================== REQUESTS ====================

@api_catalog_bp.route('/requests', methods=['GET'])
def get_requests():
    """
    Lista requests de um endpoint
    """
    try:
        endpoint_id = request.args.get('endpoint_id')
        if not endpoint_id:
            return jsonify({
                'success': False,
                'message': 'endpoint_id é obrigatório'
            }), 400
        
        result = service.get_requests(endpoint_id)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500


@api_catalog_bp.route('/requests', methods=['POST'])
def create_request():
    """
    Cria uma request
    """
    try:
        data = request.get_json()
        result = service.create_request(
            endpoint_id=data.get('endpoint_id'),
            method=data.get('method'),
            name=data.get('name'),
            content_type=data.get('content_type', 'application/json'),
            auth_id=data.get('auth_id'),
            headers=data.get('headers'),
            body_template=data.get('body_template'),
            query_params=data.get('query_params')
        )
        return jsonify(result), 201 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500


# ==================== TEST ====================

@api_catalog_bp.route('/test/<int:request_id>', methods=['POST'])
def test_request(request_id):
    """
    Testa uma request
    """
    try:
        data = request.get_json() or {}
        result = service.test_request(
            request_id=request_id,
            body_data=data.get('body'),
            query_data=data.get('query_params'),
            headers_data=data.get('headers')
        )
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500


@api_catalog_bp.route('/test-params/<int:request_id>', methods=['GET'])
def get_test_params(request_id):
    """
    Obtém os últimos parâmetros de teste salvos
    """
    try:
        result = service.get_test_parameters(request_id)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro: {str(e)}'
        }), 500
