import requests
import json
import uuid
from src.database.db_manager import DatabaseManager


class APICatalogService:
    """
    Service layer para gerenciar catálogo de APIs
    """
    
    def __init__(self):
        """
        Inicializa o serviço
        """
        self.db = DatabaseManager()
    
    # ==================== OWNERS ====================
    
    def create_owner(self, name, description=None):
        """
        Cria um novo dono de API
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO api_owners (name, description)
                VALUES (?, ?)
            ''', (name, description))
            
            conn.commit()
            owner_id = cursor.lastrowid
            conn.close()
            
            return {
                'success': True,
                'message': 'Dono criado com sucesso',
                'owner_id': owner_id
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao criar dono: {str(e)}'
            }
    
    def get_owners(self):
        """
        Lista todos os donos
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM api_owners ORDER BY name')
            rows = cursor.fetchall()
            conn.close()
            
            owners = []
            for row in rows:
                owners.append({
                    'id': row['id'],
                    'name': row['name'],
                    'description': row['description'],
                    'created_at': row['created_at']
                })
            
            return {
                'success': True,
                'owners': owners
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao listar donos: {str(e)}'
            }
    
    # ==================== APIS ====================
    
    def create_api(self, name, owner_id, base_url=None, description=None):
        """
        Cria uma nova API
        """
        try:
            api_id = str(uuid.uuid4())
            
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO apis (id, name, owner_id, base_url, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (api_id, name, owner_id, base_url, description))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'API criada com sucesso',
                'api_id': api_id
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao criar API: {str(e)}'
            }
    
    def get_apis(self, owner_id=None):
        """
        Lista APIs (opcionalmente filtradas por dono)
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            if owner_id:
                cursor.execute('''
                    SELECT a.*, o.name as owner_name
                    FROM apis a
                    JOIN api_owners o ON a.owner_id = o.id
                    WHERE a.owner_id = ?
                    ORDER BY a.name
                ''', (owner_id,))
            else:
                cursor.execute('''
                    SELECT a.*, o.name as owner_name
                    FROM apis a
                    JOIN api_owners o ON a.owner_id = o.id
                    ORDER BY a.name
                ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            apis = []
            for row in rows:
                apis.append({
                    'id': row['id'],
                    'name': row['name'],
                    'owner_id': row['owner_id'],
                    'owner_name': row['owner_name'],
                    'base_url': row['base_url'],
                    'description': row['description'],
                    'created_at': row['created_at']
                })
            
            return {
                'success': True,
                'apis': apis
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao listar APIs: {str(e)}'
            }
    
    def get_api(self, api_id):
        """
        Obtém detalhes de uma API
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT a.*, o.name as owner_name
                FROM apis a
                JOIN api_owners o ON a.owner_id = o.id
                WHERE a.id = ?
            ''', (api_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'success': True,
                    'api': {
                        'id': row['id'],
                        'name': row['name'],
                        'owner_id': row['owner_id'],
                        'owner_name': row['owner_name'],
                        'base_url': row['base_url'],
                        'description': row['description'],
                        'created_at': row['created_at']
                    }
                }
            else:
                return {
                    'success': False,
                    'message': 'API não encontrada'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao obter API: {str(e)}'
            }
    
    def delete_api(self, api_id):
        """
        Deleta uma API
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM apis WHERE id = ?', (api_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return {
                    'success': True,
                    'message': 'API deletada com sucesso'
                }
            else:
                conn.close()
                return {
                    'success': False,
                    'message': 'API não encontrada'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao deletar API: {str(e)}'
            }
    
    # ==================== AUTHENTICATIONS ====================
    
    def create_authentication(self, owner_id, name, auth_type, auth_config, token_field=None):
        """
        Cria uma autenticação
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO api_authentications (owner_id, name, auth_type, auth_config, token_field)
                VALUES (?, ?, ?, ?, ?)
            ''', (owner_id, name, auth_type, json.dumps(auth_config), token_field))
            
            conn.commit()
            auth_id = cursor.lastrowid
            conn.close()
            
            return {
                'success': True,
                'message': 'Autenticação criada com sucesso',
                'auth_id': auth_id
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao criar autenticação: {str(e)}'
            }
    
    def get_authentications(self, owner_id=None):
        """
        Lista autenticações
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            if owner_id:
                cursor.execute('''
                    SELECT a.*, o.name as owner_name
                    FROM api_authentications a
                    JOIN api_owners o ON a.owner_id = o.id
                    WHERE a.owner_id = ?
                    ORDER BY a.name
                ''', (owner_id,))
            else:
                cursor.execute('''
                    SELECT a.*, o.name as owner_name
                    FROM api_authentications a
                    JOIN api_owners o ON a.owner_id = o.id
                    ORDER BY a.name
                ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            auths = []
            for row in rows:
                auths.append({
                    'id': row['id'],
                    'owner_id': row['owner_id'],
                    'owner_name': row['owner_name'],
                    'name': row['name'],
                    'auth_type': row['auth_type'],
                    'auth_config': json.loads(row['auth_config']) if row['auth_config'] else {},
                    'token_field': row['token_field'],
                    'created_at': row['created_at']
                })
            
            return {
                'success': True,
                'authentications': auths
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao listar autenticações: {str(e)}'
            }
    
    # ==================== ENDPOINTS ====================
    
    def create_endpoint(self, api_id, path, description=None):
        """
        Cria um endpoint
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO api_endpoints (api_id, path, description)
                VALUES (?, ?, ?)
            ''', (api_id, path, description))
            
            conn.commit()
            endpoint_id = cursor.lastrowid
            conn.close()
            
            return {
                'success': True,
                'message': 'Endpoint criado com sucesso',
                'endpoint_id': endpoint_id
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao criar endpoint: {str(e)}'
            }
    
    def get_endpoints(self, api_id):
        """
        Lista endpoints de uma API
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM api_endpoints
                WHERE api_id = ?
                ORDER BY path
            ''', (api_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            endpoints = []
            for row in rows:
                endpoints.append({
                    'id': row['id'],
                    'api_id': row['api_id'],
                    'path': row['path'],
                    'description': row['description'],
                    'created_at': row['created_at']
                })
            
            return {
                'success': True,
                'endpoints': endpoints
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao listar endpoints: {str(e)}'
            }
    
    # ==================== REQUESTS ====================
    
    def create_request(self, endpoint_id, method, name=None, content_type='application/json',
                      auth_id=None, headers=None, body_template=None, query_params=None):
        """
        Cria uma request
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO api_requests (endpoint_id, method, name, content_type, auth_id, 
                                        headers, body_template, query_params)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (endpoint_id, method, name, content_type, auth_id,
                  json.dumps(headers) if headers else None,
                  body_template,
                  json.dumps(query_params) if query_params else None))
            
            conn.commit()
            request_id = cursor.lastrowid
            conn.close()
            
            return {
                'success': True,
                'message': 'Request criada com sucesso',
                'request_id': request_id
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao criar request: {str(e)}'
            }
    
    def get_requests(self, endpoint_id):
        """
        Lista requests de um endpoint
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT r.*, a.name as auth_name
                FROM api_requests r
                LEFT JOIN api_authentications a ON r.auth_id = a.id
                WHERE r.endpoint_id = ?
                ORDER BY r.method, r.name
            ''', (endpoint_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            requests_list = []
            for row in rows:
                requests_list.append({
                    'id': row['id'],
                    'endpoint_id': row['endpoint_id'],
                    'method': row['method'],
                    'name': row['name'],
                    'content_type': row['content_type'],
                    'auth_id': row['auth_id'],
                    'auth_name': row['auth_name'],
                    'headers': json.loads(row['headers']) if row['headers'] else {},
                    'body_template': row['body_template'],
                    'query_params': json.loads(row['query_params']) if row['query_params'] else {},
                    'created_at': row['created_at']
                })
            
            return {
                'success': True,
                'requests': requests_list
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao listar requests: {str(e)}'
            }
    
    # ==================== TEST REQUEST ====================
    
    def test_request(self, request_id, body_data=None, query_data=None, headers_data=None):
        """
        Executa um teste de request
        """
        try:
            # Busca dados da request
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT r.*, e.path, a.base_url, auth.auth_config, auth.token_field
                FROM api_requests r
                JOIN api_endpoints e ON r.endpoint_id = e.id
                JOIN apis a ON e.api_id = a.id
                LEFT JOIN api_authentications auth ON r.auth_id = auth.id
                WHERE r.id = ?
            ''', (request_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return {
                    'success': False,
                    'message': 'Request não encontrada'
                }
            
            # Salva parâmetros de teste
            self.db.save_test_parameters(
                request_id=request_id,
                body=json.dumps(body_data) if body_data else None,
                query_params=json.dumps(query_data) if query_data else None,
                headers=json.dumps(headers_data) if headers_data else None
            )
            
            # Monta a URL
            base_url = row['base_url'] or ''
            path = row['path']
            url = f"{base_url}{path}"
            
            # Prepara headers
            headers = json.loads(row['headers']) if row['headers'] else {}
            headers['Content-Type'] = row['content_type']
            
            # Adiciona headers customizados do teste
            if headers_data:
                headers.update(headers_data)
            
            # Adiciona autenticação se houver
            if row['auth_config']:
                auth_config = json.loads(row['auth_config'])
                # Aqui você pode implementar diferentes tipos de auth
                if 'token' in auth_config:
                    headers['Authorization'] = f"Bearer {auth_config['token']}"
            
            # Prepara query params
            params = query_data if query_data else (json.loads(row['query_params']) if row['query_params'] else {})
            
            # Prepara body
            data = None
            if row['method'] in ['POST', 'PUT', 'PATCH']:
                if body_data:
                    data = body_data
                elif row['body_template']:
                    data = row['body_template']
            
            # Executa request
            response = requests.request(
                method=row['method'],
                url=url,
                headers=headers,
                params=params,
                json=data if row['content_type'] == 'application/json' else None,
                data=data if row['content_type'] != 'application/json' else None,
                timeout=30
            )
            
            return {
                'success': True,
                'response': {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'body': response.text,
                    'json': response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                }
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Erro na requisição: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao testar request: {str(e)}'
            }
    
    def get_test_parameters(self, request_id):
        """
        Obtém os últimos parâmetros de teste salvos
        """
        return self.db.get_test_parameters(request_id)
