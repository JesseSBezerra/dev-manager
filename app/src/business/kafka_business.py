"""
Business layer para Kafka
"""
from src.service.kafka_service import KafkaService
from src.database.db_manager import DatabaseManager
import json

class KafkaBusiness:
    def __init__(self):
        self.service = KafkaService()
        self.db = DatabaseManager()
    
    # ==================== OWNERS ====================
    
    def get_owners(self):
        """Lista todos os donos"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM kafka_owners ORDER BY name')
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
            
            return {'success': True, 'owners': owners}
        except Exception as e:
            return {'success': False, 'message': f'Erro: {str(e)}'}
    
    def create_owner(self, name, description=None):
        """Cria um dono"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                'INSERT INTO kafka_owners (name, description) VALUES (?, ?)',
                (name, description)
            )
            
            conn.commit()
            owner_id = cursor.lastrowid
            conn.close()
            
            return {'success': True, 'message': 'Dono criado com sucesso', 'owner_id': owner_id}
        except Exception as e:
            return {'success': False, 'message': f'Erro: {str(e)}'}
    
    def delete_owner(self, owner_id):
        """Deleta um dono"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM kafka_owners WHERE id = ?', (owner_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return {'success': True, 'message': 'Dono deletado com sucesso'}
            else:
                conn.close()
                return {'success': False, 'message': 'Dono não encontrado'}
        except Exception as e:
            return {'success': False, 'message': f'Erro: {str(e)}'}
    
    # ==================== AUTHENTICATIONS ====================
    
    def get_authentications(self):
        """Lista todas as autenticações"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT a.*, o.name as owner_name
                FROM kafka_authentications a
                JOIN kafka_owners o ON a.owner_id = o.id
                ORDER BY o.name, a.name
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
                    'sasl_mechanism': row['sasl_mechanism'],
                    'username': row['username'],
                    'created_at': row['created_at']
                })
            
            return {'success': True, 'authentications': auths}
        except Exception as e:
            return {'success': False, 'message': f'Erro: {str(e)}'}
    
    def create_authentication(self, owner_id, name, auth_type, sasl_mechanism=None, 
                            username=None, password=None, ssl_ca_cert=None, 
                            ssl_client_cert=None, ssl_client_key=None):
        """Cria uma autenticação"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO kafka_authentications 
                (owner_id, name, auth_type, sasl_mechanism, username, password, 
                 ssl_ca_cert, ssl_client_cert, ssl_client_key)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (owner_id, name, auth_type, sasl_mechanism, username, password,
                  ssl_ca_cert, ssl_client_cert, ssl_client_key))
            
            conn.commit()
            auth_id = cursor.lastrowid
            conn.close()
            
            return {'success': True, 'message': 'Autenticação criada com sucesso', 'auth_id': auth_id}
        except Exception as e:
            return {'success': False, 'message': f'Erro: {str(e)}'}
    
    def delete_authentication(self, auth_id):
        """Deleta uma autenticação"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM kafka_authentications WHERE id = ?', (auth_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return {'success': True, 'message': 'Autenticação deletada com sucesso'}
            else:
                conn.close()
                return {'success': False, 'message': 'Autenticação não encontrada'}
        except Exception as e:
            return {'success': False, 'message': f'Erro: {str(e)}'}
    
    # ==================== SCHEMAS ====================
    
    def get_schemas(self):
        """Lista todos os schemas"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.*, o.name as owner_name
                FROM kafka_schemas s
                JOIN kafka_owners o ON s.owner_id = o.id
                ORDER BY o.name, s.name
            ''')
            rows = cursor.fetchall()
            conn.close()
            
            schemas = []
            for row in rows:
                schemas.append({
                    'id': row['id'],
                    'owner_id': row['owner_id'],
                    'owner_name': row['owner_name'],
                    'name': row['name'],
                    'schema_type': row['schema_type'],
                    'schema_content': row['schema_content'],
                    'description': row['description'],
                    'created_at': row['created_at']
                })
            
            return {'success': True, 'schemas': schemas}
        except Exception as e:
            return {'success': False, 'message': f'Erro: {str(e)}'}
    
    def create_schema(self, owner_id, name, schema_type, schema_content, description=None):
        """Cria um schema"""
        try:
            # Valida schema se for Avro
            if schema_type == 'avro':
                validation = self.service.validate_avro_schema(schema_content)
                if not validation['success']:
                    return validation
            
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO kafka_schemas (owner_id, name, schema_type, schema_content, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (owner_id, name, schema_type, schema_content, description))
            
            conn.commit()
            schema_id = cursor.lastrowid
            conn.close()
            
            return {'success': True, 'message': 'Schema criado com sucesso', 'schema_id': schema_id}
        except Exception as e:
            return {'success': False, 'message': f'Erro: {str(e)}'}
    
    def delete_schema(self, schema_id):
        """Deleta um schema"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM kafka_schemas WHERE id = ?', (schema_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return {'success': True, 'message': 'Schema deletado com sucesso'}
            else:
                conn.close()
                return {'success': False, 'message': 'Schema não encontrado'}
        except Exception as e:
            return {'success': False, 'message': f'Erro: {str(e)}'}
    
    # ==================== CLUSTERS ====================
    
    def get_clusters(self):
        """Lista todos os clusters"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT c.*, o.name as owner_name, a.name as auth_name
                FROM kafka_clusters c
                JOIN kafka_owners o ON c.owner_id = o.id
                LEFT JOIN kafka_authentications a ON c.auth_id = a.id
                ORDER BY o.name, c.name
            ''')
            rows = cursor.fetchall()
            conn.close()
            
            clusters = []
            for row in rows:
                clusters.append({
                    'id': row['id'],
                    'owner_id': row['owner_id'],
                    'owner_name': row['owner_name'],
                    'name': row['name'],
                    'bootstrap_servers': row['bootstrap_servers'],
                    'auth_id': row['auth_id'],
                    'auth_name': row['auth_name'],
                    'description': row['description'],
                    'created_at': row['created_at']
                })
            
            return {'success': True, 'clusters': clusters}
        except Exception as e:
            return {'success': False, 'message': f'Erro: {str(e)}'}
    
    def create_cluster(self, owner_id, name, bootstrap_servers, auth_id=None, description=None):
        """Cria um cluster"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO kafka_clusters (owner_id, name, bootstrap_servers, auth_id, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (owner_id, name, bootstrap_servers, auth_id, description))
            
            conn.commit()
            cluster_id = cursor.lastrowid
            conn.close()
            
            return {'success': True, 'message': 'Cluster criado com sucesso', 'cluster_id': cluster_id}
        except Exception as e:
            return {'success': False, 'message': f'Erro: {str(e)}'}
    
    def delete_cluster(self, cluster_id):
        """Deleta um cluster"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM kafka_clusters WHERE id = ?', (cluster_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return {'success': True, 'message': 'Cluster deletado com sucesso'}
            else:
                conn.close()
                return {'success': False, 'message': 'Cluster não encontrado'}
        except Exception as e:
            return {'success': False, 'message': f'Erro: {str(e)}'}
    
    # ==================== TOPICS ====================
    
    def get_topics(self, cluster_id):
        """Lista tópicos de um cluster"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT t.*, s.name as schema_name, s.schema_type
                FROM kafka_topics t
                LEFT JOIN kafka_schemas s ON t.schema_id = s.id
                WHERE t.cluster_id = ?
                ORDER BY t.topic_name
            ''', (cluster_id,))
            rows = cursor.fetchall()
            conn.close()
            
            topics = []
            for row in rows:
                topics.append({
                    'id': row['id'],
                    'cluster_id': row['cluster_id'],
                    'topic_name': row['topic_name'],
                    'schema_id': row['schema_id'],
                    'schema_name': row['schema_name'],
                    'schema_type': row['schema_type'],
                    'partitions': row['partitions'],
                    'replication_factor': row['replication_factor'],
                    'description': row['description'],
                    'last_message_payload': row['last_message_payload'],
                    'last_message_headers': row['last_message_headers'],
                    'created_at': row['created_at']
                })
            
            return {'success': True, 'topics': topics}
        except Exception as e:
            return {'success': False, 'message': f'Erro: {str(e)}'}
    
    def create_topic(self, cluster_id, topic_name, schema_id=None, partitions=1, 
                    replication_factor=1, description=None):
        """Cria um tópico"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO kafka_topics 
                (cluster_id, topic_name, schema_id, partitions, replication_factor, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (cluster_id, topic_name, schema_id, partitions, replication_factor, description))
            
            conn.commit()
            topic_id = cursor.lastrowid
            conn.close()
            
            return {'success': True, 'message': 'Tópico criado com sucesso', 'topic_id': topic_id}
        except Exception as e:
            return {'success': False, 'message': f'Erro: {str(e)}'}
    
    def delete_topic(self, topic_id):
        """Deleta um tópico"""
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM kafka_topics WHERE id = ?', (topic_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return {'success': True, 'message': 'Tópico deletado com sucesso'}
            else:
                conn.close()
                return {'success': False, 'message': 'Tópico não encontrado'}
        except Exception as e:
            return {'success': False, 'message': f'Erro: {str(e)}'}
    
    # ==================== PUBLISH ====================
    
    def publish_message(self, topic_id, payload, key=None, headers=None):
        """Publica mensagem em tópico"""
        try:
            # Busca dados do tópico e cluster
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT t.*, c.bootstrap_servers, c.auth_id,
                       a.auth_type, a.sasl_mechanism, a.username, a.password,
                       a.ssl_ca_cert, a.ssl_client_cert, a.ssl_client_key,
                       s.schema_type, s.schema_content
                FROM kafka_topics t
                JOIN kafka_clusters c ON t.cluster_id = c.id
                LEFT JOIN kafka_authentications a ON c.auth_id = a.id
                LEFT JOIN kafka_schemas s ON t.schema_id = s.id
                WHERE t.id = ?
            ''', (topic_id,))
            
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                return {'success': False, 'message': 'Tópico não encontrado'}
            
            # Prepara configuração de autenticação
            auth_config = None
            if row['auth_id']:
                auth_config = {
                    'auth_type': row['auth_type'],
                    'sasl_mechanism': row['sasl_mechanism'],
                    'username': row['username'],
                    'password': row['password'],
                    'ssl_ca_cert': row['ssl_ca_cert'],
                    'ssl_client_cert': row['ssl_client_cert'],
                    'ssl_client_key': row['ssl_client_key']
                }
            
            # Valida payload com schema se houver
            if row['schema_id'] and row['schema_type'] == 'avro':
                try:
                    self.service.serialize_avro(row['schema_content'], payload)
                except Exception as e:
                    conn.close()
                    return {'success': False, 'message': f'Payload inválido para schema: {str(e)}'}
            
            # Envia mensagem
            result = self.service.send_message(
                bootstrap_servers=row['bootstrap_servers'],
                topic=row['topic_name'],
                message=payload,
                key=key,
                headers=headers,
                auth_config=auth_config
            )
            
            # Salva última mensagem
            if result['success']:
                cursor.execute('''
                    UPDATE kafka_topics 
                    SET last_message_payload = ?, 
                        last_message_headers = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (json.dumps(payload), json.dumps(headers) if headers else None, topic_id))
                conn.commit()
            
            conn.close()
            return result
            
        except Exception as e:
            return {'success': False, 'message': f'Erro: {str(e)}'}
