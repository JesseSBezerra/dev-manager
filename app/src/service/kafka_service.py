"""
Service para Kafka
"""
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import json
import avro.schema
import avro.io
import io

class KafkaService:
    def __init__(self):
        """
        Inicializa o serviço Kafka
        """
        self.producers = {}
    
    def create_producer(self, bootstrap_servers, auth_config=None):
        """
        Cria um producer Kafka
        
        Args:
            bootstrap_servers: Lista de servidores bootstrap
            auth_config: Configuração de autenticação
        
        Returns:
            KafkaProducer
        """
        try:
            config = {
                'bootstrap_servers': bootstrap_servers.split(','),
                'value_serializer': lambda v: json.dumps(v).encode('utf-8'),
                'key_serializer': lambda k: k.encode('utf-8') if k else None
            }
            
            # Adiciona autenticação se fornecida
            if auth_config:
                if auth_config.get('auth_type') == 'SASL_SSL':
                    config['security_protocol'] = 'SASL_SSL'
                    config['sasl_mechanism'] = auth_config.get('sasl_mechanism', 'PLAIN')
                    config['sasl_plain_username'] = auth_config.get('username')
                    config['sasl_plain_password'] = auth_config.get('password')
                elif auth_config.get('auth_type') == 'SSL':
                    config['security_protocol'] = 'SSL'
                    if auth_config.get('ssl_ca_cert'):
                        config['ssl_cafile'] = auth_config.get('ssl_ca_cert')
                    if auth_config.get('ssl_client_cert'):
                        config['ssl_certfile'] = auth_config.get('ssl_client_cert')
                    if auth_config.get('ssl_client_key'):
                        config['ssl_keyfile'] = auth_config.get('ssl_client_key')
            
            producer = KafkaProducer(**config)
            return producer
            
        except Exception as e:
            raise Exception(f'Erro ao criar producer: {str(e)}')
    
    def send_message(self, bootstrap_servers, topic, message, key=None, headers=None, auth_config=None):
        """
        Envia mensagem para tópico Kafka
        
        Args:
            bootstrap_servers: Servidores bootstrap
            topic: Nome do tópico
            message: Mensagem (dict)
            key: Chave da mensagem (opcional)
            headers: Headers da mensagem (opcional)
            auth_config: Configuração de autenticação
        
        Returns:
            dict: Resultado da operação
        """
        try:
            producer = self.create_producer(bootstrap_servers, auth_config)
            
            # Prepara headers
            kafka_headers = None
            if headers:
                kafka_headers = [(k, v.encode('utf-8')) for k, v in headers.items()]
            
            # Envia mensagem
            future = producer.send(
                topic,
                value=message,
                key=key,
                headers=kafka_headers
            )
            
            # Aguarda confirmação
            record_metadata = future.get(timeout=10)
            
            producer.flush()
            producer.close()
            
            return {
                'success': True,
                'message': 'Mensagem enviada com sucesso',
                'topic': record_metadata.topic,
                'partition': record_metadata.partition,
                'offset': record_metadata.offset
            }
            
        except KafkaError as e:
            return {
                'success': False,
                'message': f'Erro Kafka: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro: {str(e)}'
            }
    
    def validate_avro_schema(self, schema_content):
        """
        Valida schema Avro
        
        Args:
            schema_content: Conteúdo do schema (JSON string)
        
        Returns:
            dict: Resultado da validação
        """
        try:
            schema_dict = json.loads(schema_content)
            avro.schema.parse(json.dumps(schema_dict))
            
            return {
                'success': True,
                'message': 'Schema Avro válido'
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'message': f'JSON inválido: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Schema Avro inválido: {str(e)}'
            }
    
    def serialize_avro(self, schema_content, data):
        """
        Serializa dados usando schema Avro
        
        Args:
            schema_content: Conteúdo do schema
            data: Dados a serializar
        
        Returns:
            bytes: Dados serializados
        """
        try:
            schema_dict = json.loads(schema_content)
            schema = avro.schema.parse(json.dumps(schema_dict))
            
            writer = avro.io.DatumWriter(schema)
            bytes_writer = io.BytesIO()
            encoder = avro.io.BinaryEncoder(bytes_writer)
            writer.write(data, encoder)
            
            return bytes_writer.getvalue()
            
        except Exception as e:
            raise Exception(f'Erro ao serializar Avro: {str(e)}')
    
    def test_connection(self, bootstrap_servers, auth_config=None):
        """
        Testa conexão com cluster Kafka
        
        Args:
            bootstrap_servers: Servidores bootstrap
            auth_config: Configuração de autenticação
        
        Returns:
            dict: Resultado do teste
        """
        try:
            producer = self.create_producer(bootstrap_servers, auth_config)
            
            # Tenta obter metadados
            metadata = producer.partitions_for('__test__')
            
            producer.close()
            
            return {
                'success': True,
                'message': 'Conexão estabelecida com sucesso'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro na conexão: {str(e)}'
            }
