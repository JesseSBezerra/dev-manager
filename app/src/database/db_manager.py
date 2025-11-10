import sqlite3
import os
from datetime import datetime


class DatabaseManager:
    """
    Gerenciador do banco SQLite para queries salvas e favoritos
    """
    
    def __init__(self):
        """
        Inicializa o banco de dados
        """
        # Caminho do banco de dados
        db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        os.makedirs(db_dir, exist_ok=True)
        
        self.db_path = os.path.join(db_dir, 'cloudwatch_queries.db')
        self._create_tables()
    
    def _get_connection(self):
        """
        Obtém conexão com o banco
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
        return conn
    
    def _create_tables(self):
        """
        Cria as tabelas se não existirem
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tabela de queries salvas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                log_group_name TEXT NOT NULL,
                query_string TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, log_group_name)
            )
        ''')
        
        # Tabela de log groups favoritos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorite_log_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_group_name TEXT NOT NULL UNIQUE,
                alias TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de secrets favoritos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorite_secrets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                secret_name TEXT NOT NULL UNIQUE,
                alias TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de parameters favoritos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorite_parameters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parameter_name TEXT NOT NULL UNIQUE,
                alias TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de clusters ECS favoritos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorite_ecs_clusters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cluster_name TEXT NOT NULL UNIQUE,
                alias TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de instâncias RDS favoritas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorite_rds_instances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instance_identifier TEXT NOT NULL UNIQUE,
                alias TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabelas do API Catalog
        
        # Tabela de donos de APIs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_owners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de APIs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS apis (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                owner_id INTEGER NOT NULL,
                base_url TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES api_owners(id)
            )
        ''')
        
        # Tabela de autenticações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_authentications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                auth_type TEXT NOT NULL,
                auth_config TEXT,
                token_field TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES api_owners(id),
                UNIQUE(owner_id, name)
            )
        ''')
        
        # Tabela de endpoints
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_endpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_id TEXT NOT NULL,
                path TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (api_id) REFERENCES apis(id) ON DELETE CASCADE,
                UNIQUE(api_id, path)
            )
        ''')
        
        # Tabela de requests
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint_id INTEGER NOT NULL,
                method TEXT NOT NULL,
                name TEXT,
                content_type TEXT DEFAULT 'application/json',
                auth_id INTEGER,
                headers TEXT,
                body_template TEXT,
                query_params TEXT,
                last_test_body TEXT,
                last_test_query TEXT,
                last_test_headers TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (endpoint_id) REFERENCES api_endpoints(id) ON DELETE CASCADE,
                FOREIGN KEY (auth_id) REFERENCES api_authentications(id),
                UNIQUE(endpoint_id, method, name)
            )
        ''')
        
        # ==================== KAFKA CATALOG ====================
        
        # Tabela de donos de Kafka
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kafka_owners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de autenticações Kafka
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kafka_authentications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                auth_type TEXT NOT NULL,
                sasl_mechanism TEXT,
                username TEXT,
                password TEXT,
                ssl_ca_cert TEXT,
                ssl_client_cert TEXT,
                ssl_client_key TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES kafka_owners(id),
                UNIQUE(owner_id, name)
            )
        ''')
        
        # Tabela de schemas Kafka (Avro/JSON)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kafka_schemas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                schema_type TEXT NOT NULL,
                schema_content TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES kafka_owners(id),
                UNIQUE(owner_id, name)
            )
        ''')
        
        # Tabela de clusters Kafka
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kafka_clusters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                bootstrap_servers TEXT NOT NULL,
                auth_id INTEGER,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES kafka_owners(id),
                FOREIGN KEY (auth_id) REFERENCES kafka_authentications(id),
                UNIQUE(owner_id, name)
            )
        ''')
        
        # Tabela de tópicos Kafka
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kafka_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cluster_id INTEGER NOT NULL,
                topic_name TEXT NOT NULL,
                schema_id INTEGER,
                partitions INTEGER DEFAULT 1,
                replication_factor INTEGER DEFAULT 1,
                description TEXT,
                last_message_payload TEXT,
                last_message_headers TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cluster_id) REFERENCES kafka_clusters(id) ON DELETE CASCADE,
                FOREIGN KEY (schema_id) REFERENCES kafka_schemas(id),
                UNIQUE(cluster_id, topic_name)
            )
        ''')
        
        # Tabela de túneis SSH salvos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_tunnels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                bastion_id TEXT NOT NULL,
                db_host TEXT NOT NULL,
                db_port INTEGER NOT NULL,
                db_name TEXT NOT NULL,
                db_user TEXT NOT NULL,
                db_password TEXT,
                db_type TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de comandos SQL salvos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_sql_commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tunnel_id INTEGER,
                name TEXT NOT NULL,
                sql_command TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tunnel_id) REFERENCES saved_tunnels(id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ==================== QUERIES SALVAS ====================
    
    def save_query(self, name, log_group_name, query_string, description=None):
        """
        Salva uma query
        
        Args:
            name (str): Nome da query
            log_group_name (str): Nome do log group
            query_string (str): Query SQL
            description (str): Descrição (opcional)
        
        Returns:
            dict: Resultado da operação
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO saved_queries (name, log_group_name, query_string, description)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(name, log_group_name) 
                DO UPDATE SET 
                    query_string = excluded.query_string,
                    description = excluded.description,
                    updated_at = CURRENT_TIMESTAMP
            ''', (name, log_group_name, query_string, description))
            
            conn.commit()
            query_id = cursor.lastrowid
            conn.close()
            
            return {
                'success': True,
                'message': f'Query "{name}" salva com sucesso',
                'id': query_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao salvar query: {str(e)}'
            }
    
    def get_queries_by_log_group(self, log_group_name):
        """
        Obtém todas as queries de um log group
        
        Args:
            log_group_name (str): Nome do log group
        
        Returns:
            dict: Lista de queries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, log_group_name, query_string, description, 
                       created_at, updated_at
                FROM saved_queries
                WHERE log_group_name = ?
                ORDER BY name
            ''', (log_group_name,))
            
            rows = cursor.fetchall()
            conn.close()
            
            queries = []
            for row in rows:
                queries.append({
                    'id': row['id'],
                    'name': row['name'],
                    'log_group_name': row['log_group_name'],
                    'query_string': row['query_string'],
                    'description': row['description'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            
            return {
                'success': True,
                'queries': queries,
                'count': len(queries)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao buscar queries: {str(e)}'
            }
    
    def get_all_queries(self):
        """
        Obtém todas as queries salvas
        
        Returns:
            dict: Lista de queries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, log_group_name, query_string, description, 
                       created_at, updated_at
                FROM saved_queries
                ORDER BY log_group_name, name
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            queries = []
            for row in rows:
                queries.append({
                    'id': row['id'],
                    'name': row['name'],
                    'log_group_name': row['log_group_name'],
                    'query_string': row['query_string'],
                    'description': row['description'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            
            return {
                'success': True,
                'queries': queries,
                'count': len(queries)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao buscar queries: {str(e)}'
            }
    
    def get_query_by_id(self, query_id):
        """
        Obtém uma query específica
        
        Args:
            query_id (int): ID da query
        
        Returns:
            dict: Query
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, log_group_name, query_string, description, 
                       created_at, updated_at
                FROM saved_queries
                WHERE id = ?
            ''', (query_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'success': True,
                    'query': {
                        'id': row['id'],
                        'name': row['name'],
                        'log_group_name': row['log_group_name'],
                        'query_string': row['query_string'],
                        'description': row['description'],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    }
                }
            else:
                return {
                    'success': False,
                    'message': 'Query não encontrada'
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao buscar query: {str(e)}'
            }
    
    def delete_query(self, query_id):
        """
        Deleta uma query
        
        Args:
            query_id (int): ID da query
        
        Returns:
            dict: Resultado da operação
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM saved_queries WHERE id = ?', (query_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return {
                    'success': True,
                    'message': 'Query deletada com sucesso'
                }
            else:
                conn.close()
                return {
                    'success': False,
                    'message': 'Query não encontrada'
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao deletar query: {str(e)}'
            }
    
    # ==================== FAVORITOS ====================
    
    def add_favorite(self, log_group_name, alias=None):
        """
        Adiciona log group aos favoritos
        
        Args:
            log_group_name (str): Nome do log group
            alias (str): Apelido (opcional)
        
        Returns:
            dict: Resultado da operação
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO favorite_log_groups (log_group_name, alias)
                VALUES (?, ?)
                ON CONFLICT(log_group_name) 
                DO UPDATE SET alias = excluded.alias
            ''', (log_group_name, alias))
            
            conn.commit()
            favorite_id = cursor.lastrowid
            conn.close()
            
            return {
                'success': True,
                'message': 'Log group adicionado aos favoritos',
                'id': favorite_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao adicionar favorito: {str(e)}'
            }
    
    def remove_favorite(self, log_group_name):
        """
        Remove log group dos favoritos
        
        Args:
            log_group_name (str): Nome do log group
        
        Returns:
            dict: Resultado da operação
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM favorite_log_groups WHERE log_group_name = ?', (log_group_name,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return {
                    'success': True,
                    'message': 'Log group removido dos favoritos'
                }
            else:
                conn.close()
                return {
                    'success': False,
                    'message': 'Log group não está nos favoritos'
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao remover favorito: {str(e)}'
            }
    
    def get_favorites(self):
        """
        Obtém todos os log groups favoritos
        
        Returns:
            dict: Lista de favoritos
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, log_group_name, alias, created_at
                FROM favorite_log_groups
                ORDER BY log_group_name
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            favorites = []
            for row in rows:
                favorites.append({
                    'id': row['id'],
                    'log_group_name': row['log_group_name'],
                    'alias': row['alias'],
                    'created_at': row['created_at']
                })
            
            return {
                'success': True,
                'favorites': favorites,
                'count': len(favorites)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao buscar favoritos: {str(e)}'
            }
    
    def is_favorite(self, log_group_name):
        """
        Verifica se um log group é favorito
        
        Args:
            log_group_name (str): Nome do log group
        
        Returns:
            bool: True se é favorito
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM favorite_log_groups
                WHERE log_group_name = ?
            ''', (log_group_name,))
            
            row = cursor.fetchone()
            conn.close()
            
            return row['count'] > 0
            
        except Exception as e:
            return False
    
    # ==================== SECRETS FAVORITOS ====================
    
    def add_favorite_secret(self, secret_name, alias=None):
        """
        Adiciona secret aos favoritos
        
        Args:
            secret_name (str): Nome do secret
            alias (str): Apelido (opcional)
        
        Returns:
            dict: Resultado da operação
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO favorite_secrets (secret_name, alias)
                VALUES (?, ?)
                ON CONFLICT(secret_name) 
                DO UPDATE SET alias = excluded.alias
            ''', (secret_name, alias))
            
            conn.commit()
            favorite_id = cursor.lastrowid
            conn.close()
            
            return {
                'success': True,
                'message': 'Secret adicionado aos favoritos',
                'id': favorite_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao adicionar favorito: {str(e)}'
            }
    
    def remove_favorite_secret(self, secret_name):
        """
        Remove secret dos favoritos
        
        Args:
            secret_name (str): Nome do secret
        
        Returns:
            dict: Resultado da operação
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM favorite_secrets WHERE secret_name = ?', (secret_name,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return {
                    'success': True,
                    'message': 'Secret removido dos favoritos'
                }
            else:
                conn.close()
                return {
                    'success': False,
                    'message': 'Secret não está nos favoritos'
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao remover favorito: {str(e)}'
            }
    
    def get_favorite_secrets(self):
        """
        Obtém todos os secrets favoritos
        
        Returns:
            dict: Lista de favoritos
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, secret_name, alias, created_at
                FROM favorite_secrets
                ORDER BY secret_name
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            favorites = []
            for row in rows:
                favorites.append({
                    'id': row['id'],
                    'secret_name': row['secret_name'],
                    'alias': row['alias'],
                    'created_at': row['created_at']
                })
            
            return {
                'success': True,
                'favorites': favorites,
                'count': len(favorites)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao buscar favoritos: {str(e)}'
            }
    
    def is_favorite_secret(self, secret_name):
        """
        Verifica se um secret é favorito
        
        Args:
            secret_name (str): Nome do secret
        
        Returns:
            bool: True se é favorito
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM favorite_secrets
                WHERE secret_name = ?
            ''', (secret_name,))
            
            row = cursor.fetchone()
            conn.close()
            
            return row['count'] > 0
            
        except Exception as e:
            return False
    
    # ==================== PARAMETERS FAVORITOS ====================
    
    def add_favorite_parameter(self, parameter_name, alias=None):
        """
        Adiciona parameter aos favoritos
        
        Args:
            parameter_name (str): Nome do parameter
            alias (str): Apelido (opcional)
        
        Returns:
            dict: Resultado da operação
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO favorite_parameters (parameter_name, alias)
                VALUES (?, ?)
                ON CONFLICT(parameter_name) 
                DO UPDATE SET alias = excluded.alias
            ''', (parameter_name, alias))
            
            conn.commit()
            favorite_id = cursor.lastrowid
            conn.close()
            
            return {
                'success': True,
                'message': 'Parameter adicionado aos favoritos',
                'id': favorite_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao adicionar favorito: {str(e)}'
            }
    
    def remove_favorite_parameter(self, parameter_name):
        """
        Remove parameter dos favoritos
        
        Args:
            parameter_name (str): Nome do parameter
        
        Returns:
            dict: Resultado da operação
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM favorite_parameters WHERE parameter_name = ?', (parameter_name,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return {
                    'success': True,
                    'message': 'Parameter removido dos favoritos'
                }
            else:
                conn.close()
                return {
                    'success': False,
                    'message': 'Parameter não está nos favoritos'
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao remover favorito: {str(e)}'
            }
    
    def get_favorite_parameters(self):
        """
        Obtém todos os parameters favoritos
        
        Returns:
            dict: Lista de favoritos
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, parameter_name, alias, created_at
                FROM favorite_parameters
                ORDER BY parameter_name
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            favorites = []
            for row in rows:
                favorites.append({
                    'id': row['id'],
                    'parameter_name': row['parameter_name'],
                    'alias': row['alias'],
                    'created_at': row['created_at']
                })
            
            return {
                'success': True,
                'favorites': favorites,
                'count': len(favorites)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao buscar favoritos: {str(e)}'
            }
    
    def is_favorite_parameter(self, parameter_name):
        """
        Verifica se um parameter é favorito
        
        Args:
            parameter_name (str): Nome do parameter
        
        Returns:
            bool: True se é favorito
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM favorite_parameters
                WHERE parameter_name = ?
            ''', (parameter_name,))
            
            row = cursor.fetchone()
            conn.close()
            
            return row['count'] > 0
            
        except Exception as e:
            return False
    
    # ==================== TÚNEIS SSH SALVOS ====================
    
    def save_tunnel(self, name, bastion_id, db_host, db_port, db_name, db_user, db_type, db_password=None, description=None):
        """
        Salva um túnel SSH
        
        Args:
            name: Nome do túnel
            bastion_id: ID da instância bastion
            db_host: Host do banco de dados
            db_port: Porta do banco de dados
            db_name: Nome do banco de dados
            db_user: Usuário do banco de dados
            db_type: Tipo do banco (mysql, postgres)
            db_password: Senha do banco (opcional)
            description: Descrição (opcional)
        
        Returns:
            dict: Resultado da operação
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Verifica se já existe
            cursor.execute('SELECT id FROM saved_tunnels WHERE name = ?', (name,))
            existing = cursor.fetchone()
            
            if existing:
                # Atualiza
                cursor.execute('''
                    UPDATE saved_tunnels 
                    SET bastion_id = ?, db_host = ?, db_port = ?, db_name = ?, 
                        db_user = ?, db_password = ?, db_type = ?, description = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE name = ?
                ''', (bastion_id, db_host, db_port, db_name, db_user, db_password, db_type, description, name))
                message = 'Túnel atualizado com sucesso'
            else:
                # Insere
                cursor.execute('''
                    INSERT INTO saved_tunnels (name, bastion_id, db_host, db_port, db_name, db_user, db_password, db_type, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, bastion_id, db_host, db_port, db_name, db_user, db_password, db_type, description))
                message = 'Túnel salvo com sucesso'
            
            conn.commit()
            tunnel_id = existing['id'] if existing else cursor.lastrowid
            conn.close()
            
            return {
                'success': True,
                'message': message,
                'tunnel_id': tunnel_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao salvar túnel: {str(e)}'
            }
    
    def get_saved_tunnels(self):
        """
        Lista todos os túneis salvos
        
        Returns:
            dict: Lista de túneis
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM saved_tunnels 
                ORDER BY name
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            tunnels = []
            for row in rows:
                tunnels.append({
                    'id': row['id'],
                    'name': row['name'],
                    'bastion_id': row['bastion_id'],
                    'db_host': row['db_host'],
                    'db_port': row['db_port'],
                    'db_name': row['db_name'],
                    'db_user': row['db_user'],
                    'db_password': row['db_password'],
                    'db_type': row['db_type'],
                    'description': row['description'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            
            return {
                'success': True,
                'tunnels': tunnels
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao listar túneis: {str(e)}',
                'tunnels': []
            }
    
    def get_tunnel(self, tunnel_id):
        """
        Obtém um túnel específico
        
        Args:
            tunnel_id: ID do túnel
        
        Returns:
            dict: Dados do túnel
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM saved_tunnels WHERE id = ?', (tunnel_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'success': True,
                    'tunnel': {
                        'id': row['id'],
                        'name': row['name'],
                        'bastion_id': row['bastion_id'],
                        'db_host': row['db_host'],
                        'db_port': row['db_port'],
                        'db_name': row['db_name'],
                        'db_user': row['db_user'],
                        'db_password': row['db_password'],
                        'db_type': row['db_type'],
                        'description': row['description'],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    }
                }
            else:
                return {
                    'success': False,
                    'message': 'Túnel não encontrado'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao obter túnel: {str(e)}'
            }
    
    def delete_tunnel(self, tunnel_id):
        """
        Deleta um túnel salvo
        
        Args:
            tunnel_id: ID do túnel
        
        Returns:
            dict: Resultado da operação
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM saved_tunnels WHERE id = ?', (tunnel_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return {
                    'success': True,
                    'message': 'Túnel deletado com sucesso'
                }
            else:
                conn.close()
                return {
                    'success': False,
                    'message': 'Túnel não encontrado'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao deletar túnel: {str(e)}'
            }
    
    # ==================== COMANDOS SQL SALVOS ====================
    
    def save_sql_command(self, tunnel_id, name, sql_command, description=None):
        """
        Salva um comando SQL
        
        Args:
            tunnel_id: ID do túnel (opcional)
            name: Nome do comando
            sql_command: Comando SQL
            description: Descrição (opcional)
        
        Returns:
            dict: Resultado da operação
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO saved_sql_commands (tunnel_id, name, sql_command, description)
                VALUES (?, ?, ?, ?)
            ''', (tunnel_id, name, sql_command, description))
            
            conn.commit()
            command_id = cursor.lastrowid
            conn.close()
            
            return {
                'success': True,
                'message': 'Comando salvo com sucesso',
                'command_id': command_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao salvar comando: {str(e)}'
            }
    
    def get_sql_commands(self, tunnel_id=None):
        """
        Lista comandos SQL salvos
        
        Args:
            tunnel_id: ID do túnel para filtrar (opcional)
        
        Returns:
            dict: Lista de comandos
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if tunnel_id:
                cursor.execute('''
                    SELECT * FROM saved_sql_commands 
                    WHERE tunnel_id = ? OR tunnel_id IS NULL
                    ORDER BY created_at DESC
                ''', (tunnel_id,))
            else:
                cursor.execute('''
                    SELECT * FROM saved_sql_commands 
                    ORDER BY created_at DESC
                ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            commands = []
            for row in rows:
                commands.append({
                    'id': row['id'],
                    'tunnel_id': row['tunnel_id'],
                    'name': row['name'],
                    'sql_command': row['sql_command'],
                    'description': row['description'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            
            return {
                'success': True,
                'commands': commands
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao listar comandos: {str(e)}',
                'commands': []
            }
    
    def delete_sql_command(self, command_id):
        """
        Deleta um comando SQL salvo
        
        Args:
            command_id: ID do comando
        
        Returns:
            dict: Resultado da operação
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM saved_sql_commands WHERE id = ?', (command_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return {
                    'success': True,
                    'message': 'Comando deletado com sucesso'
                }
            else:
                conn.close()
                return {
                    'success': False,
                    'message': 'Comando não encontrado'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao deletar comando: {str(e)}'
            }
    
    # ==================== ECS FAVORITOS ====================
    
    def add_favorite_ecs_cluster(self, cluster_name, alias=None):
        """
        Adiciona cluster ECS aos favoritos
        
        Args:
            cluster_name (str): Nome do cluster
            alias (str): Apelido (opcional)
        
        Returns:
            dict: Resultado da operação
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO favorite_ecs_clusters (cluster_name, alias)
                VALUES (?, ?)
                ON CONFLICT(cluster_name) 
                DO UPDATE SET alias = excluded.alias
            ''', (cluster_name, alias))
            
            conn.commit()
            favorite_id = cursor.lastrowid
            conn.close()
            
            return {
                'success': True,
                'message': 'Cluster adicionado aos favoritos',
                'id': favorite_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao adicionar favorito: {str(e)}'
            }
    
    def remove_favorite_ecs_cluster(self, cluster_name):
        """
        Remove cluster ECS dos favoritos
        
        Args:
            cluster_name (str): Nome do cluster
        
        Returns:
            dict: Resultado da operação
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM favorite_ecs_clusters WHERE cluster_name = ?', (cluster_name,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return {
                    'success': True,
                    'message': 'Cluster removido dos favoritos'
                }
            else:
                conn.close()
                return {
                    'success': False,
                    'message': 'Cluster não está nos favoritos'
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao remover favorito: {str(e)}'
            }
    
    def get_favorite_ecs_clusters(self):
        """
        Obtém todos os clusters ECS favoritos
        
        Returns:
            dict: Lista de favoritos
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, cluster_name, alias, created_at
                FROM favorite_ecs_clusters
                ORDER BY cluster_name
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            favorites = []
            for row in rows:
                favorites.append({
                    'id': row['id'],
                    'cluster_name': row['cluster_name'],
                    'alias': row['alias'],
                    'created_at': row['created_at']
                })
            
            return {
                'success': True,
                'favorites': favorites
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao obter favoritos: {str(e)}',
                'favorites': []
            }
    
    def is_favorite_ecs_cluster(self, cluster_name):
        """
        Verifica se um cluster ECS está nos favoritos
        
        Args:
            cluster_name (str): Nome do cluster
        
        Returns:
            bool: True se está nos favoritos
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM favorite_ecs_clusters
                WHERE cluster_name = ?
            ''', (cluster_name,))
            
            row = cursor.fetchone()
            conn.close()
            
            return row['count'] > 0
            
        except Exception as e:
            return False
    
    # ==================== RDS FAVORITOS ====================
    
    def add_favorite_rds_instance(self, instance_identifier, alias=None):
        """
        Adiciona instância RDS aos favoritos
        
        Args:
            instance_identifier (str): Identificador da instância
            alias (str): Apelido (opcional)
        
        Returns:
            dict: Resultado da operação
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO favorite_rds_instances (instance_identifier, alias)
                VALUES (?, ?)
                ON CONFLICT(instance_identifier) 
                DO UPDATE SET alias = excluded.alias
            ''', (instance_identifier, alias))
            
            conn.commit()
            favorite_id = cursor.lastrowid
            conn.close()
            
            return {
                'success': True,
                'message': 'Instância adicionada aos favoritos',
                'id': favorite_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao adicionar favorito: {str(e)}'
            }
    
    def remove_favorite_rds_instance(self, instance_identifier):
        """
        Remove instância RDS dos favoritos
        
        Args:
            instance_identifier (str): Identificador da instância
        
        Returns:
            dict: Resultado da operação
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM favorite_rds_instances WHERE instance_identifier = ?', (instance_identifier,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return {
                    'success': True,
                    'message': 'Instância removida dos favoritos'
                }
            else:
                conn.close()
                return {
                    'success': False,
                    'message': 'Instância não está nos favoritos'
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao remover favorito: {str(e)}'
            }
    
    def get_favorite_rds_instances(self):
        """
        Obtém todas as instâncias RDS favoritas
        
        Returns:
            dict: Lista de favoritos
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, instance_identifier, alias, created_at
                FROM favorite_rds_instances
                ORDER BY instance_identifier
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            favorites = []
            for row in rows:
                favorites.append({
                    'id': row['id'],
                    'instance_identifier': row['instance_identifier'],
                    'alias': row['alias'],
                    'created_at': row['created_at']
                })
            
            return {
                'success': True,
                'favorites': favorites
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao obter favoritos: {str(e)}',
                'favorites': []
            }
    
    def is_favorite_rds_instance(self, instance_identifier):
        """
        Verifica se uma instância RDS está nos favoritos
        
        Args:
            instance_identifier (str): Identificador da instância
        
        Returns:
            bool: True se está nos favoritos
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM favorite_rds_instances
                WHERE instance_identifier = ?
            ''', (instance_identifier,))
            
            row = cursor.fetchone()
            conn.close()
            
            return row['count'] > 0
            
        except Exception as e:
            return False
    
    # ==================== API TEST PARAMETERS ====================
    
    def save_test_parameters(self, request_id, body=None, query_params=None, headers=None):
        """
        Salva os últimos parâmetros de teste de um request
        
        Args:
            request_id: ID do request
            body: Body JSON (string)
            query_params: Query parameters JSON (string)
            headers: Headers JSON (string)
        
        Returns:
            dict: Resultado da operação
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE api_requests 
                SET last_test_body = ?, 
                    last_test_query = ?, 
                    last_test_headers = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (body, query_params, headers, request_id))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Parâmetros salvos com sucesso'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao salvar parâmetros: {str(e)}'
            }
    
    def get_test_parameters(self, request_id):
        """
        Obtém os últimos parâmetros de teste de um request
        
        Args:
            request_id: ID do request
        
        Returns:
            dict: Parâmetros salvos
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT last_test_body, last_test_query, last_test_headers
                FROM api_requests
                WHERE id = ?
            ''', (request_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'success': True,
                    'body': row['last_test_body'],
                    'query_params': row['last_test_query'],
                    'headers': row['last_test_headers']
                }
            else:
                return {
                    'success': False,
                    'message': 'Request não encontrado'
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao obter parâmetros: {str(e)}'
            }
