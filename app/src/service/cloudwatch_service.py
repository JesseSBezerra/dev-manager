import boto3
from boto3 import Session
from botocore.exceptions import ClientError
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class CloudWatchLogsService:
    """
    Service layer para gerenciar operações com CloudWatch Logs usando boto3
    """
    
    def __init__(self):
        """
        Inicializa a conexão com CloudWatch Logs usando boto3
        """
        self.aws_region = os.getenv('AWS_REGION', 'sa-east-1')
        
        session = Session()
        
        # Usa a cadeia de credenciais padrão (AWS Toolkit, CLI, etc.)
        self.logs_client = session.client(
            'logs',
            region_name=self.aws_region
        )
    
    def list_log_groups(self, prefix=None):
        """
        Lista todos os log groups
        
        Args:
            prefix (str): Prefixo para filtrar log groups (opcional)
        
        Returns:
            dict: Lista de log groups ou erro
        """
        try:
            log_groups = []
            params = {}
            
            if prefix:
                params['logGroupNamePrefix'] = prefix
            
            paginator = self.logs_client.get_paginator('describe_log_groups')
            
            for page in paginator.paginate(**params):
                for log_group in page.get('logGroups', []):
                    log_groups.append(log_group)
            
            return {
                'success': True,
                'log_groups': log_groups,
                'count': len(log_groups)
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao listar log groups: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def list_log_streams(self, log_group_name, limit=50):
        """
        Lista log streams de um log group
        
        Args:
            log_group_name (str): Nome do log group
            limit (int): Número máximo de streams (padrão 50)
        
        Returns:
            dict: Lista de log streams ou erro
        """
        try:
            response = self.logs_client.describe_log_streams(
                logGroupName=log_group_name,
                orderBy='LastEventTime',
                descending=True,
                limit=limit
            )
            
            return {
                'success': True,
                'log_streams': response.get('logStreams', []),
                'count': len(response.get('logStreams', []))
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao listar log streams: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def get_log_events(self, log_group_name, log_stream_name, limit=100, start_time=None, end_time=None):
        """
        Obtém eventos de log de um stream específico
        
        Args:
            log_group_name (str): Nome do log group
            log_stream_name (str): Nome do log stream
            limit (int): Número máximo de eventos (padrão 100)
            start_time (int): Timestamp de início (opcional)
            end_time (int): Timestamp de fim (opcional)
        
        Returns:
            dict: Eventos de log ou erro
        """
        try:
            params = {
                'logGroupName': log_group_name,
                'logStreamName': log_stream_name,
                'limit': limit,
                'startFromHead': False  # Mais recentes primeiro
            }
            
            if start_time:
                params['startTime'] = start_time
            if end_time:
                params['endTime'] = end_time
            
            response = self.logs_client.get_log_events(**params)
            
            return {
                'success': True,
                'events': response.get('events', []),
                'count': len(response.get('events', []))
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao obter eventos: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def filter_log_events(self, log_group_name, filter_pattern=None, start_time=None, end_time=None, limit=100):
        """
        Filtra eventos de log usando um padrão
        
        Args:
            log_group_name (str): Nome do log group
            filter_pattern (str): Padrão de filtro (opcional)
            start_time (int): Timestamp de início (opcional)
            end_time (int): Timestamp de fim (opcional)
            limit (int): Número máximo de eventos
        
        Returns:
            dict: Eventos filtrados ou erro
        """
        try:
            params = {
                'logGroupName': log_group_name,
                'limit': limit
            }
            
            if filter_pattern:
                params['filterPattern'] = filter_pattern
            if start_time:
                params['startTime'] = start_time
            if end_time:
                params['endTime'] = end_time
            
            response = self.logs_client.filter_log_events(**params)
            
            return {
                'success': True,
                'events': response.get('events', []),
                'count': len(response.get('events', []))
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao filtrar eventos: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def start_query(self, log_group_names, query_string, start_time, end_time, limit=1000):
        """
        Inicia uma query no CloudWatch Logs Insights
        
        Args:
            log_group_names (list): Lista de log groups
            query_string (str): Query em CloudWatch Insights syntax
            start_time (int): Timestamp de início
            end_time (int): Timestamp de fim
            limit (int): Limite de resultados
        
        Returns:
            dict: ID da query ou erro
        """
        try:
            response = self.logs_client.start_query(
                logGroupNames=log_group_names if isinstance(log_group_names, list) else [log_group_names],
                startTime=start_time,
                endTime=end_time,
                queryString=query_string,
                limit=limit
            )
            
            return {
                'success': True,
                'query_id': response['queryId']
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao iniciar query: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def get_query_results(self, query_id):
        """
        Obtém resultados de uma query do Logs Insights
        
        Args:
            query_id (str): ID da query
        
        Returns:
            dict: Resultados da query ou erro
        """
        try:
            response = self.logs_client.get_query_results(queryId=query_id)
            
            return {
                'success': True,
                'status': response['status'],
                'results': response.get('results', []),
                'statistics': response.get('statistics', {})
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao obter resultados: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def execute_query_and_wait(self, log_group_names, query_string, start_time, end_time, limit=1000, max_wait=30):
        """
        Executa uma query e aguarda os resultados
        
        Args:
            log_group_names (list): Lista de log groups
            query_string (str): Query string
            start_time (int): Timestamp de início
            end_time (int): Timestamp de fim
            limit (int): Limite de resultados
            max_wait (int): Tempo máximo de espera em segundos
        
        Returns:
            dict: Resultados da query ou erro
        """
        try:
            # Inicia a query
            start_result = self.start_query(log_group_names, query_string, start_time, end_time, limit)
            
            if not start_result['success']:
                return start_result
            
            query_id = start_result['query_id']
            
            # Aguarda resultados
            elapsed = 0
            while elapsed < max_wait:
                result = self.get_query_results(query_id)
                
                if not result['success']:
                    return result
                
                status = result['status']
                
                if status == 'Complete':
                    return {
                        'success': True,
                        'results': result['results'],
                        'statistics': result.get('statistics', {}),
                        'query_id': query_id
                    }
                elif status == 'Failed' or status == 'Cancelled':
                    return {
                        'success': False,
                        'message': f'Query {status.lower()}'
                    }
                
                # Aguarda 1 segundo antes de verificar novamente
                time.sleep(1)
                elapsed += 1
            
            return {
                'success': False,
                'message': f'Query timeout após {max_wait} segundos',
                'query_id': query_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao executar query: {str(e)}'
            }
    
    def get_log_group_info(self, log_group_name):
        """
        Obtém informações detalhadas de um log group
        
        Args:
            log_group_name (str): Nome do log group
        
        Returns:
            dict: Informações do log group ou erro
        """
        try:
            response = self.logs_client.describe_log_groups(
                logGroupNamePrefix=log_group_name,
                limit=1
            )
            
            log_groups = response.get('logGroups', [])
            
            if not log_groups:
                return {
                    'success': False,
                    'message': f'Log group "{log_group_name}" não encontrado'
                }
            
            return {
                'success': True,
                'log_group': log_groups[0]
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao obter informações: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
