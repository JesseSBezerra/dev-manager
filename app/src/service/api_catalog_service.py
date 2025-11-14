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
    
    def create_api(self, name, owner_id, base_url=None, description=None, content_type='application/json', auth_id=None, default_headers=None):
        """
        Cria uma nova API
        """
        try:
            api_id = str(uuid.uuid4())
            
            # Converter headers para JSON string se fornecido
            headers_json = json.dumps(default_headers) if default_headers else None
            
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO apis (id, name, owner_id, base_url, description, content_type, auth_id, default_headers)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (api_id, name, owner_id, base_url, description, content_type, auth_id, headers_json))
            
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
                # Verificar se as colunas existem
                try:
                    content_type = row['content_type']
                except (KeyError, IndexError):
                    content_type = 'application/json'
                
                try:
                    auth_id = row['auth_id']
                except (KeyError, IndexError):
                    auth_id = None
                
                try:
                    default_headers = json.loads(row['default_headers']) if row['default_headers'] else None
                except (KeyError, IndexError):
                    default_headers = None
                
                apis.append({
                    'id': row['id'],
                    'name': row['name'],
                    'owner_id': row['owner_id'],
                    'owner_name': row['owner_name'],
                    'base_url': row['base_url'],
                    'description': row['description'],
                    'content_type': content_type,
                    'auth_id': auth_id,
                    'default_headers': default_headers,
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
                # Verificar se as colunas existem
                try:
                    content_type = row['content_type']
                except (KeyError, IndexError):
                    content_type = 'application/json'
                
                try:
                    auth_id = row['auth_id']
                except (KeyError, IndexError):
                    auth_id = None
                
                try:
                    default_headers = json.loads(row['default_headers']) if row['default_headers'] else None
                except (KeyError, IndexError):
                    default_headers = None
                
                return {
                    'success': True,
                    'api': {
                        'id': row['id'],
                        'name': row['name'],
                        'owner_id': row['owner_id'],
                        'owner_name': row['owner_name'],
                        'base_url': row['base_url'],
                        'description': row['description'],
                        'content_type': content_type,
                        'auth_id': auth_id,
                        'default_headers': default_headers,
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
    
    def test_oauth2_authentication(self, url, method='POST', body=None, headers=None):
        """
        Testa uma autenticação OAuth2
        """
        try:
            if not url:
                return {
                    'success': False,
                    'message': 'URL é obrigatória'
                }
            
            # Preparar headers
            request_headers = headers or {}
            if 'Content-Type' not in request_headers:
                request_headers['Content-Type'] = 'application/json'
            
            # Fazer a requisição
            if method.upper() == 'POST':
                response = requests.post(url, json=body, headers=request_headers, timeout=30)
            elif method.upper() == 'GET':
                response = requests.get(url, params=body, headers=request_headers, timeout=30)
            else:
                return {
                    'success': False,
                    'message': f'Método {method} não suportado'
                }
            
            # Processar resposta
            try:
                response_json = response.json()
            except:
                response_json = None
            
            return {
                'success': True,
                'response': {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'json': response_json,
                    'body': response.text
                }
            }
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'message': 'Timeout na requisição (30s)'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Erro na requisição: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao testar OAuth2: {str(e)}'
            }
    
    def delete_authentication(self, auth_id):
        """
        Deleta uma autenticação
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            # Verificar se existe
            cursor.execute('SELECT name FROM api_authentications WHERE id = ?', (auth_id,))
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                return {
                    'success': False,
                    'message': 'Autenticação não encontrada'
                }
            
            # Deletar
            cursor.execute('DELETE FROM api_authentications WHERE id = ?', (auth_id,))
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': f'Autenticação "{row["name"]}" deletada com sucesso'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao deletar autenticação: {str(e)}'
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
    
    def delete_endpoint(self, endpoint_id):
        """
        Deleta um endpoint e todas as suas requests
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            # Deletar requests primeiro (foreign key)
            cursor.execute('DELETE FROM api_requests WHERE endpoint_id = ?', (endpoint_id,))
            
            # Deletar endpoint
            cursor.execute('DELETE FROM api_endpoints WHERE id = ?', (endpoint_id,))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Endpoint e suas requests deletados com sucesso'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao deletar endpoint: {str(e)}'
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
                  json.dumps(body_template) if body_template else None,
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
    
    def delete_request(self, request_id):
        """
        Deleta uma request
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM api_requests WHERE id = ?', (request_id,))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Request deletada com sucesso'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao deletar request: {str(e)}'
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
                    'body_template': json.loads(row['body_template']) if row['body_template'] else {},
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
    
    # ==================== HELPER METHODS ====================
    
    def _camel_to_snake(self, name):
        """
        Converte camelCase para snake_case
        accessToken -> access_token
        """
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    
    def _snake_to_camel(self, name):
        """
        Converte snake_case para camelCase
        access_token -> accessToken
        """
        components = name.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
    
    def _get_nested_value(self, data, path):
        """
        Obtém valor aninhado de um dicionário usando dot notation
        Exemplo: 'user.name' retorna data['user']['name']
        """
        keys = path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def _replace_auth_variables(self, headers, auth_tokens):
        """
        Substitui variáveis ${campo} nos headers pelos valores reais
        """
        import re
        
        replaced_headers = {}
        pattern = r'\$\{([^}]+)\}'
        
        print(f"[DEBUG] _replace_auth_variables - Iniciando substituição")
        print(f"[DEBUG] Pattern regex: {pattern}")
        
        for key, value in headers.items():
            print(f"[DEBUG] Processando header: {key} = {value}")
            
            if isinstance(value, str):
                # Procurar por ${campo} no valor
                matches = re.findall(pattern, value)
                print(f"[DEBUG] Variáveis encontradas em '{key}': {matches}")
                
                def replace_match(match):
                    field_name = match.group(1)
                    replacement = auth_tokens.get(field_name, match.group(0))
                    print(f"[DEBUG] Substituindo ${{{field_name}}} por: {replacement[:20] if isinstance(replacement, str) and len(replacement) > 20 else replacement}")
                    return str(replacement)
                
                replaced_value = re.sub(pattern, replace_match, value)
                replaced_headers[key] = replaced_value
                print(f"[DEBUG] Valor final de '{key}': {replaced_value[:50] if len(replaced_value) > 50 else replaced_value}...")
            else:
                replaced_headers[key] = value
        
        return replaced_headers
    
    # ==================== TEST REQUEST ====================
    
    def test_request(self, request_id, body_data=None, query_data=None, headers_data=None, path_variables=None):
        """
        Executa um teste de request
        """
        try:
            # Busca dados da request
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT r.*, e.path, a.base_url, a.default_headers, a.auth_id as api_auth_id,
                       auth.auth_type, auth.auth_config, auth.token_field,
                       req_auth.auth_type as req_auth_type, req_auth.auth_config as req_auth_config, 
                       req_auth.token_field as req_token_field
                FROM api_requests r
                JOIN api_endpoints e ON r.endpoint_id = e.id
                JOIN apis a ON e.api_id = a.id
                LEFT JOIN api_authentications auth ON a.auth_id = auth.id
                LEFT JOIN api_authentications req_auth ON r.auth_id = req_auth.id
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
            
            # Monta a URL e substitui path variables
            base_url = row['base_url'] or ''
            path = row['path']
            
            # Substituir path variables (ex: /pessoas/{id} -> /pessoas/123)
            if path_variables:
                for var_name, var_value in path_variables.items():
                    path = path.replace(f'{{{var_name}}}', str(var_value))
            
            url = f"{base_url}{path}"
            print(f"[DEBUG] URL final após substituição de path variables: {url}")
            
            # Determinar qual autenticação usar (request sobrescreve API)
            auth_type = row['req_auth_type'] if row['req_auth_type'] else row['auth_type']
            auth_config = row['req_auth_config'] if row['req_auth_config'] else row['auth_config']
            token_field = row['req_token_field'] if row['req_token_field'] else row['token_field']
            
            print(f"[DEBUG] Auth type detectado: {auth_type}")
            print(f"[DEBUG] Auth config existe: {bool(auth_config)}")
            
            # Executar autenticação OAuth2 se necessário
            auth_tokens = {}
            if auth_type == 'oauth2' and auth_config:
                print(f"[DEBUG] Executando OAuth2...")
                try:
                    auth_config_dict = json.loads(auth_config)
                    print(f"[DEBUG] Auth config: {auth_config_dict}")
                    
                    oauth_result = self.test_oauth2_authentication(
                        url=auth_config_dict.get('url'),
                        method=auth_config_dict.get('method', 'POST'),
                        body=auth_config_dict.get('body'),
                        headers=auth_config_dict.get('headers')
                    )
                    
                    print(f"[DEBUG] OAuth2 result success: {oauth_result.get('success')}")
                    print(f"[DEBUG] OAuth2 result completo: {oauth_result}")
                    
                    if oauth_result.get('success') and oauth_result.get('response'):
                        # Extrair campos selecionados
                        selected_fields = auth_config_dict.get('selected_fields', [])
                        
                        # A resposta vem em oauth_result['response']['json']
                        response_data = oauth_result['response'].get('json') or oauth_result['response'].get('body')
                        
                        print(f"[DEBUG] Selected fields: {selected_fields}")
                        print(f"[DEBUG] Response data keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'not a dict'}")
                        print(f"[DEBUG] Response data completo: {response_data}")
                        
                        for field in selected_fields:
                            # Navegar pelo JSON usando dot notation
                            value = self._get_nested_value(response_data, field)
                            if value is not None:
                                auth_tokens[field] = value
                                print(f"[DEBUG] Token extraído - {field}: {value[:20] if isinstance(value, str) and len(str(value)) > 20 else value}")
                                
                                # Também adicionar variações do nome (camelCase <-> snake_case)
                                # accessToken -> access_token
                                snake_case = self._camel_to_snake(field)
                                if snake_case != field:
                                    auth_tokens[snake_case] = value
                                    print(f"[DEBUG] Também adicionado como: {snake_case}")
                                
                                # access_token -> accessToken
                                camel_case = self._snake_to_camel(field)
                                if camel_case != field:
                                    auth_tokens[camel_case] = value
                                    print(f"[DEBUG] Também adicionado como: {camel_case}")
                            else:
                                print(f"[DEBUG] Campo '{field}' não encontrado na resposta")
                        
                        print(f"[DEBUG] Auth tokens coletados: {list(auth_tokens.keys())}")
                except Exception as e:
                    print(f"[ERROR] Erro ao executar OAuth2: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Prepara headers começando com os padrão da API
            headers = {}
            
            # 1. Headers padrão da API
            if row['default_headers']:
                try:
                    api_headers = json.loads(row['default_headers'])
                    headers.update(api_headers)
                except:
                    pass
            
            # 2. Headers da request
            if row['headers']:
                try:
                    request_headers = json.loads(row['headers'])
                    headers.update(request_headers)
                except:
                    pass
            
            # 3. Content-Type
            headers['Content-Type'] = row['content_type']
            
            # 4. Headers customizados do teste
            if headers_data:
                headers.update(headers_data)
            
            # 5. Substituir variáveis ${campo} pelos valores da autenticação
            print(f"[DEBUG] ========== SUBSTITUIÇÃO DE VARIÁVEIS ==========")
            print(f"[DEBUG] Headers antes da substituição: {headers}")
            print(f"[DEBUG] Auth tokens disponíveis: {auth_tokens}")
            print(f"[DEBUG] Quantidade de tokens: {len(auth_tokens)}")
            
            # SEMPRE executar substituição para debug
            headers = self._replace_auth_variables(headers, auth_tokens)
            print(f"[DEBUG] Headers após substituição: {headers}")
            print(f"[DEBUG] ===============================================")
            
            # Prepara query params
            params = query_data if query_data else (json.loads(row['query_params']) if row['query_params'] else {})
            
            # Prepara body
            data = None
            if row['method'] in ['POST', 'PUT', 'PATCH']:
                if body_data:
                    data = body_data
                elif row['body_template']:
                    data = json.loads(row['body_template'])
            
            # Executa request
            import time
            start_time = time.time()
            
            response = requests.request(
                method=row['method'],
                url=url,
                headers=headers,
                params=params,
                json=data if row['content_type'] == 'application/json' else None,
                data=data if row['content_type'] != 'application/json' else None,
                timeout=30
            )
            
            elapsed_time = round(time.time() - start_time, 3)
            
            # Tentar parsear resposta como JSON
            response_body = None
            try:
                response_body = response.json()
            except:
                response_body = response.text
            
            return {
                'success': True,
                'status_code': response.status_code,
                'response_headers': dict(response.headers),
                'response_body': response_body,
                'elapsed_time': elapsed_time,
                'url': url
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
