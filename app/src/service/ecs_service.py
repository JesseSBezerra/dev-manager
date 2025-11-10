import boto3
from boto3 import Session
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

load_dotenv()


class ECSService:
    """
    Service layer para gerenciar operações com ECS (Elastic Container Service) usando boto3
    """
    
    def __init__(self):
        """
        Inicializa a conexão com ECS usando boto3
        """
        self.aws_region = os.getenv('AWS_REGION', 'sa-east-1')
        

        session = Session()
        
        # Se as credenciais estiverem definidas no .env, usa elas
        # Caso contrário, deixa o boto3 usar a cadeia de credenciais padrão
        # Usa a cadeia de credenciais padrão (AWS Toolkit, CLI, etc.)
        self.ecs_client = session.client(
           'ecs',
            region_name=self.aws_region
        )
    
    def list_clusters(self):
        """
        Lista todos os clusters ECS
        
        Returns:
            dict: Lista de clusters ou erro
        """
        try:
            response = self.ecs_client.list_clusters()
            cluster_arns = response.get('clusterArns', [])
            
            # Se houver clusters, busca detalhes
            if cluster_arns:
                clusters_detail = self.ecs_client.describe_clusters(clusters=cluster_arns)
                clusters = clusters_detail.get('clusters', [])
            else:
                clusters = []
            
            return {
                'success': True,
                'clusters': clusters,
                'count': len(clusters)
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao listar clusters: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def list_services(self, cluster_name):
        """
        Lista todos os serviços de um cluster específico
        
        Args:
            cluster_name (str): Nome ou ARN do cluster
        
        Returns:
            dict: Lista de serviços ou erro
        """
        try:
            response = self.ecs_client.list_services(cluster=cluster_name)
            service_arns = response.get('serviceArns', [])
            
            # Se houver serviços, busca detalhes
            if service_arns:
                services_detail = self.ecs_client.describe_services(
                    cluster=cluster_name,
                    services=service_arns
                )
                services = services_detail.get('services', [])
            else:
                services = []
            
            return {
                'success': True,
                'services': services,
                'count': len(services)
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao listar serviços: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def list_tasks(self, cluster_name, service_name=None):
        """
        Lista todas as tasks de um cluster ou serviço específico
        
        Args:
            cluster_name (str): Nome ou ARN do cluster
            service_name (str, optional): Nome do serviço para filtrar tasks
        
        Returns:
            dict: Lista de tasks ou erro
        """
        try:
            params = {'cluster': cluster_name}
            if service_name:
                params['serviceName'] = service_name
            
            response = self.ecs_client.list_tasks(**params)
            task_arns = response.get('taskArns', [])
            
            # Se houver tasks, busca detalhes
            if task_arns:
                tasks_detail = self.ecs_client.describe_tasks(
                    cluster=cluster_name,
                    tasks=task_arns
                )
                tasks = tasks_detail.get('tasks', [])
            else:
                tasks = []
            
            return {
                'success': True,
                'tasks': tasks,
                'count': len(tasks)
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao listar tasks: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def get_cluster_details(self, cluster_name):
        """
        Obtém detalhes de um cluster específico
        
        Args:
            cluster_name (str): Nome ou ARN do cluster
        
        Returns:
            dict: Detalhes do cluster ou erro
        """
        try:
            response = self.ecs_client.describe_clusters(clusters=[cluster_name])
            clusters = response.get('clusters', [])
            
            if clusters:
                return {
                    'success': True,
                    'cluster': clusters[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Cluster não encontrado'
                }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao obter detalhes do cluster: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def get_service_details(self, cluster_name, service_name):
        """
        Obtém detalhes de um serviço específico
        
        Args:
            cluster_name (str): Nome ou ARN do cluster
            service_name (str): Nome ou ARN do serviço
        
        Returns:
            dict: Detalhes do serviço ou erro
        """
        try:
            response = self.ecs_client.describe_services(
                cluster=cluster_name,
                services=[service_name]
            )
            services = response.get('services', [])
            
            if services:
                return {
                    'success': True,
                    'service': services[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Serviço não encontrado'
                }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao obter detalhes do serviço: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def stop_service(self, cluster_name, service_name):
        """
        Para um serviço ECS (define desiredCount = 0)
        
        Args:
            cluster_name (str): Nome ou ARN do cluster
            service_name (str): Nome ou ARN do serviço
        
        Returns:
            dict: Resultado da operação
        """
        try:
            response = self.ecs_client.update_service(
                cluster=cluster_name,
                service=service_name,
                desiredCount=0
            )
            
            return {
                'success': True,
                'message': f'Serviço {service_name} parado com sucesso',
                'service': response.get('service', {})
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao parar serviço: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def start_service(self, cluster_name, service_name, desired_count):
        """
        Inicia um serviço ECS (define desiredCount)
        
        Args:
            cluster_name (str): Nome ou ARN do cluster
            service_name (str): Nome ou ARN do serviço
            desired_count (int): Número desejado de tasks
        
        Returns:
            dict: Resultado da operação
        """
        try:
            response = self.ecs_client.update_service(
                cluster=cluster_name,
                service=service_name,
                desiredCount=desired_count
            )
            
            return {
                'success': True,
                'message': f'Serviço {service_name} iniciado com {desired_count} task(s)',
                'service': response.get('service', {})
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao iniciar serviço: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def change_capacity_provider(self, cluster_name, service_name, capacity_provider):
        """
        Altera o Capacity Provider de um serviço (ex: FARGATE para FARGATE_SPOT)
        
        Args:
            cluster_name (str): Nome ou ARN do cluster
            service_name (str): Nome ou ARN do serviço
            capacity_provider (str): Nome do capacity provider (FARGATE ou FARGATE_SPOT)
        
        Returns:
            dict: Resultado da operação
        """
        try:
            # Primeiro, obtém as informações atuais do serviço
            service_info = self.get_service_details(cluster_name, service_name)
            
            if not service_info['success']:
                return service_info
            
            service = service_info['service']
            
            # Prepara a estratégia de capacity provider
            capacity_provider_strategy = [
                {
                    'capacityProvider': capacity_provider,
                    'weight': 1,
                    'base': 0
                }
            ]
            
            # Atualiza o serviço com o novo capacity provider
            response = self.ecs_client.update_service(
                cluster=cluster_name,
                service=service_name,
                capacityProviderStrategy=capacity_provider_strategy,
                forceNewDeployment=True  # Força novo deployment para aplicar mudanças
            )
            
            return {
                'success': True,
                'message': f'Capacity Provider alterado para {capacity_provider}',
                'service': response.get('service', {})
            }
            
        except ClientError as e:
            error_message = e.response['Error']['Message']
            
            # Mensagens de erro mais amigáveis
            if 'CapacityProviderStrategyItemNotFound' in str(e):
                return {
                    'success': False,
                    'message': f'Capacity Provider {capacity_provider} não está disponível neste cluster'
                }
            
            return {
                'success': False,
                'message': f'Erro ao alterar capacity provider: {error_message}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
