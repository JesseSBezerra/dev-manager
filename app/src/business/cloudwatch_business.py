from src.service.cloudwatch_service import CloudWatchLogsService
from datetime import datetime, timedelta
import re


class CloudWatchLogsBusiness:
    """
    Business layer para CloudWatch Logs - validações e regras de negócio
    """
    
    def __init__(self):
        """
        Inicializa a camada de negócio
        """
        self.service = CloudWatchLogsService()
    
    def list_all_log_groups(self, prefix=None):
        """
        Lista log groups com formatação
        
        Args:
            prefix (str): Prefixo para filtrar
        
        Returns:
            dict: Lista formatada de log groups
        """
        result = self.service.list_log_groups(prefix)
        
        if result['success']:
            # Formata os log groups
            formatted_groups = []
            for group in result['log_groups']:
                formatted_groups.append({
                    'name': group.get('logGroupName'),
                    'arn': group.get('arn'),
                    'creation_time': group.get('creationTime'),
                    'retention_days': group.get('retentionInDays', 'Nunca expira'),
                    'stored_bytes': group.get('storedBytes', 0),
                    'metric_filter_count': group.get('metricFilterCount', 0)
                })
            
            return {
                'success': True,
                'log_groups': formatted_groups,
                'count': len(formatted_groups)
            }
        
        return result
    
    def list_streams(self, log_group_name, limit=50):
        """
        Lista log streams com validações
        
        Args:
            log_group_name (str): Nome do log group
            limit (int): Limite de streams
        
        Returns:
            dict: Lista de streams
        """
        validation = self._validate_log_group_name(log_group_name)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        result = self.service.list_log_streams(log_group_name, limit)
        
        if result['success']:
            # Formata os streams
            formatted_streams = []
            for stream in result['log_streams']:
                formatted_streams.append({
                    'name': stream.get('logStreamName'),
                    'creation_time': stream.get('creationTime'),
                    'first_event_time': stream.get('firstEventTimestamp'),
                    'last_event_time': stream.get('lastEventTimestamp'),
                    'last_ingestion_time': stream.get('lastIngestionTime'),
                    'stored_bytes': stream.get('storedBytes', 0)
                })
            
            return {
                'success': True,
                'log_streams': formatted_streams,
                'count': len(formatted_streams)
            }
        
        return result
    
    def get_events(self, log_group_name, log_stream_name, limit=100, hours_ago=24):
        """
        Obtém eventos de log com validações
        
        Args:
            log_group_name (str): Nome do log group
            log_stream_name (str): Nome do log stream
            limit (int): Limite de eventos
            hours_ago (int): Horas atrás para buscar
        
        Returns:
            dict: Eventos de log
        """
        validation = self._validate_log_group_name(log_group_name)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        # Calcula timestamps
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(hours=hours_ago)).timestamp() * 1000)
        
        return self.service.get_log_events(
            log_group_name,
            log_stream_name,
            limit,
            start_time,
            end_time
        )
    
    def filter_events(self, log_group_name, filter_pattern=None, hours_ago=24, limit=100):
        """
        Filtra eventos com validações
        
        Args:
            log_group_name (str): Nome do log group
            filter_pattern (str): Padrão de filtro
            hours_ago (int): Horas atrás
            limit (int): Limite de eventos
        
        Returns:
            dict: Eventos filtrados
        """
        validation = self._validate_log_group_name(log_group_name)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        # Calcula timestamps
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(hours=hours_ago)).timestamp() * 1000)
        
        return self.service.filter_log_events(
            log_group_name,
            filter_pattern,
            start_time,
            end_time,
            limit
        )
    
    def execute_insights_query(self, log_group_names, query_string, hours_ago=24, limit=1000):
        """
        Executa query no Logs Insights com validações
        
        Args:
            log_group_names (list or str): Log groups
            query_string (str): Query
            hours_ago (int): Horas atrás
            limit (int): Limite de resultados
        
        Returns:
            dict: Resultados da query
        """
        # Converte para lista se necessário
        if isinstance(log_group_names, str):
            log_group_names = [log_group_names]
        
        # Valida log groups
        for log_group in log_group_names:
            validation = self._validate_log_group_name(log_group)
            if not validation['valid']:
                return {
                    'success': False,
                    'message': validation['message']
                }
        
        # Valida query
        validation = self._validate_query_string(query_string)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        # Calcula timestamps
        end_time = int(datetime.now().timestamp())
        start_time = int((datetime.now() - timedelta(hours=hours_ago)).timestamp())
        
        return self.service.execute_query_and_wait(
            log_group_names,
            query_string,
            start_time,
            end_time,
            limit
        )
    
    def get_log_group_details(self, log_group_name):
        """
        Obtém detalhes de um log group
        
        Args:
            log_group_name (str): Nome do log group
        
        Returns:
            dict: Detalhes do log group
        """
        validation = self._validate_log_group_name(log_group_name)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        result = self.service.get_log_group_info(log_group_name)
        
        if result['success']:
            group = result['log_group']
            
            return {
                'success': True,
                'log_group': {
                    'name': group.get('logGroupName'),
                    'arn': group.get('arn'),
                    'creation_time': group.get('creationTime'),
                    'retention_days': group.get('retentionInDays', 'Nunca expira'),
                    'stored_bytes': group.get('storedBytes', 0),
                    'metric_filter_count': group.get('metricFilterCount', 0),
                    'kms_key_id': group.get('kmsKeyId', 'Não criptografado')
                }
            }
        
        return result
    
    def _validate_log_group_name(self, name):
        """
        Valida nome do log group
        
        Returns:
            dict: Resultado da validação
        """
        if not name or name.strip() == '':
            return {
                'valid': False,
                'message': 'Nome do log group é obrigatório'
            }
        
        # Tamanho máximo
        if len(name) > 512:
            return {
                'valid': False,
                'message': 'Nome do log group muito longo (máximo 512 caracteres)'
            }
        
        # Padrão válido: alfanuméricos, -, _, /, .
        if not re.match(r'^[a-zA-Z0-9/_.-]+$', name):
            return {
                'valid': False,
                'message': 'Nome contém caracteres inválidos. Use apenas: a-z A-Z 0-9 / _ . -'
            }
        
        return {'valid': True}
    
    def _validate_query_string(self, query):
        """
        Valida query string do Logs Insights
        
        Returns:
            dict: Resultado da validação
        """
        if not query or query.strip() == '':
            return {
                'valid': False,
                'message': 'Query não pode estar vazia'
            }
        
        # Tamanho máximo
        if len(query) > 10000:
            return {
                'valid': False,
                'message': 'Query muito longa (máximo 10KB)'
            }
        
        return {'valid': True}
