from src.service.ecs_service import ECSService


class ECSBusiness:
    """
    Business layer para aplicar regras de negócio nas operações com ECS
    """
    
    def __init__(self):
        self.service = ECSService()
    
    def list_all_clusters(self):
        """
        Lista todos os clusters ECS com informações formatadas
        
        Returns:
            dict: Lista de clusters formatada
        """
        result = self.service.list_clusters()
        
        if not result['success']:
            return result
        
        # Formata os dados dos clusters para facilitar visualização
        formatted_clusters = []
        for cluster in result['clusters']:
            formatted_cluster = {
                'name': cluster.get('clusterName', 'N/A'),
                'arn': cluster.get('clusterArn', 'N/A'),
                'status': cluster.get('status', 'N/A'),
                'running_tasks': cluster.get('runningTasksCount', 0),
                'pending_tasks': cluster.get('pendingTasksCount', 0),
                'active_services': cluster.get('activeServicesCount', 0),
                'registered_instances': cluster.get('registeredContainerInstancesCount', 0),
                'statistics': cluster.get('statistics', [])
            }
            formatted_clusters.append(formatted_cluster)
        
        return {
            'success': True,
            'clusters': formatted_clusters,
            'count': len(formatted_clusters)
        }
    
    def list_cluster_services(self, cluster_name):
        """
        Lista todos os serviços de um cluster com informações formatadas
        
        Args:
            cluster_name (str): Nome do cluster
        
        Returns:
            dict: Lista de serviços formatada
        """
        if not cluster_name or cluster_name.strip() == '':
            return {
                'success': False,
                'message': 'Nome do cluster é obrigatório',
                'errors': ['Nome do cluster não pode estar vazio']
            }
        
        result = self.service.list_services(cluster_name)
        
        if not result['success']:
            return result
        
        # Formata os dados dos serviços
        formatted_services = []
        for service in result['services']:
            formatted_service = {
                'name': service.get('serviceName', 'N/A'),
                'arn': service.get('serviceArn', 'N/A'),
                'status': service.get('status', 'N/A'),
                'desired_count': service.get('desiredCount', 0),
                'running_count': service.get('runningCount', 0),
                'pending_count': service.get('pendingCount', 0),
                'launch_type': service.get('launchType', 'N/A'),
                'task_definition': self._extract_task_definition_name(
                    service.get('taskDefinition', 'N/A')
                ),
                'created_at': str(service.get('createdAt', 'N/A')),
                'load_balancers': len(service.get('loadBalancers', [])),
                'health_check_grace_period': service.get('healthCheckGracePeriodSeconds', 0)
            }
            formatted_services.append(formatted_service)
        
        return {
            'success': True,
            'services': formatted_services,
            'count': len(formatted_services),
            'cluster': cluster_name
        }
    
    def list_cluster_tasks(self, cluster_name, service_name=None):
        """
        Lista todas as tasks de um cluster ou serviço
        
        Args:
            cluster_name (str): Nome do cluster
            service_name (str, optional): Nome do serviço
        
        Returns:
            dict: Lista de tasks formatada
        """
        if not cluster_name or cluster_name.strip() == '':
            return {
                'success': False,
                'message': 'Nome do cluster é obrigatório',
                'errors': ['Nome do cluster não pode estar vazio']
            }
        
        result = self.service.list_tasks(cluster_name, service_name)
        
        if not result['success']:
            return result
        
        # Formata os dados das tasks
        formatted_tasks = []
        for task in result['tasks']:
            formatted_task = {
                'task_arn': task.get('taskArn', 'N/A'),
                'task_id': self._extract_task_id(task.get('taskArn', '')),
                'status': task.get('lastStatus', 'N/A'),
                'desired_status': task.get('desiredStatus', 'N/A'),
                'launch_type': task.get('launchType', 'N/A'),
                'task_definition': self._extract_task_definition_name(
                    task.get('taskDefinitionArn', 'N/A')
                ),
                'started_at': str(task.get('startedAt', 'N/A')),
                'cpu': task.get('cpu', 'N/A'),
                'memory': task.get('memory', 'N/A'),
                'containers': len(task.get('containers', [])),
                'health_status': task.get('healthStatus', 'UNKNOWN')
            }
            formatted_tasks.append(formatted_task)
        
        return {
            'success': True,
            'tasks': formatted_tasks,
            'count': len(formatted_tasks),
            'cluster': cluster_name,
            'service': service_name
        }
    
    def get_cluster_info(self, cluster_name):
        """
        Obtém informações detalhadas de um cluster
        
        Args:
            cluster_name (str): Nome do cluster
        
        Returns:
            dict: Informações do cluster
        """
        if not cluster_name or cluster_name.strip() == '':
            return {
                'success': False,
                'message': 'Nome do cluster é obrigatório',
                'errors': ['Nome do cluster não pode estar vazio']
            }
        
        return self.service.get_cluster_details(cluster_name)
    
    def get_service_info(self, cluster_name, service_name):
        """
        Obtém informações detalhadas de um serviço
        
        Args:
            cluster_name (str): Nome do cluster
            service_name (str): Nome do serviço
        
        Returns:
            dict: Informações do serviço
        """
        if not cluster_name or cluster_name.strip() == '':
            return {
                'success': False,
                'message': 'Nome do cluster é obrigatório',
                'errors': ['Nome do cluster não pode estar vazio']
            }
        
        if not service_name or service_name.strip() == '':
            return {
                'success': False,
                'message': 'Nome do serviço é obrigatório',
                'errors': ['Nome do serviço não pode estar vazio']
            }
        
        return self.service.get_service_details(cluster_name, service_name)
    
    def _extract_task_definition_name(self, task_definition_arn):
        """
        Extrai o nome da task definition do ARN
        
        Args:
            task_definition_arn (str): ARN da task definition
        
        Returns:
            str: Nome da task definition
        """
        if not task_definition_arn or task_definition_arn == 'N/A':
            return 'N/A'
        
        # ARN format: arn:aws:ecs:region:account:task-definition/name:revision
        parts = task_definition_arn.split('/')
        if len(parts) > 1:
            return parts[-1]
        return task_definition_arn
    
    def _extract_task_id(self, task_arn):
        """
        Extrai o ID da task do ARN
        
        Args:
            task_arn (str): ARN da task
        
        Returns:
            str: ID da task
        """
        if not task_arn:
            return 'N/A'
        
        # ARN format: arn:aws:ecs:region:account:task/cluster-name/task-id
        parts = task_arn.split('/')
        if len(parts) > 0:
            return parts[-1]
        return task_arn
    
    def stop_service(self, cluster_name, service_name):
        """
        Para um serviço ECS com validações
        
        Args:
            cluster_name (str): Nome do cluster
            service_name (str): Nome do serviço
        
        Returns:
            dict: Resultado da operação
        """
        if not cluster_name or cluster_name.strip() == '':
            return {
                'success': False,
                'message': 'Nome do cluster é obrigatório',
                'errors': ['Nome do cluster não pode estar vazio']
            }
        
        if not service_name or service_name.strip() == '':
            return {
                'success': False,
                'message': 'Nome do serviço é obrigatório',
                'errors': ['Nome do serviço não pode estar vazio']
            }
        
        return self.service.stop_service(cluster_name, service_name)
    
    def start_service(self, cluster_name, service_name, desired_count):
        """
        Inicia um serviço ECS com validações
        
        Args:
            cluster_name (str): Nome do cluster
            service_name (str): Nome do serviço
            desired_count (int): Número desejado de tasks
        
        Returns:
            dict: Resultado da operação
        """
        if not cluster_name or cluster_name.strip() == '':
            return {
                'success': False,
                'message': 'Nome do cluster é obrigatório',
                'errors': ['Nome do cluster não pode estar vazio']
            }
        
        if not service_name or service_name.strip() == '':
            return {
                'success': False,
                'message': 'Nome do serviço é obrigatório',
                'errors': ['Nome do serviço não pode estar vazio']
            }
        
        # Valida desired_count
        try:
            desired_count = int(desired_count)
            if desired_count < 0:
                return {
                    'success': False,
                    'message': 'Desired count deve ser maior ou igual a 0',
                    'errors': ['Valor inválido para desired count']
                }
            if desired_count > 100:
                return {
                    'success': False,
                    'message': 'Desired count não pode ser maior que 100',
                    'errors': ['Valor muito alto para desired count']
                }
        except (ValueError, TypeError):
            return {
                'success': False,
                'message': 'Desired count deve ser um número inteiro',
                'errors': ['Valor inválido para desired count']
            }
        
        return self.service.start_service(cluster_name, service_name, desired_count)
    
    def change_capacity_provider(self, cluster_name, service_name, capacity_provider):
        """
        Altera o Capacity Provider com validações
        
        Args:
            cluster_name (str): Nome do cluster
            service_name (str): Nome do serviço
            capacity_provider (str): Nome do capacity provider
        
        Returns:
            dict: Resultado da operação
        """
        if not cluster_name or cluster_name.strip() == '':
            return {
                'success': False,
                'message': 'Nome do cluster é obrigatório',
                'errors': ['Nome do cluster não pode estar vazio']
            }
        
        if not service_name or service_name.strip() == '':
            return {
                'success': False,
                'message': 'Nome do serviço é obrigatório',
                'errors': ['Nome do serviço não pode estar vazio']
            }
        
        # Valida capacity provider
        valid_providers = ['FARGATE', 'FARGATE_SPOT']
        if capacity_provider not in valid_providers:
            return {
                'success': False,
                'message': f'Capacity Provider inválido. Use: {", ".join(valid_providers)}',
                'errors': ['Capacity Provider inválido']
            }
        
        return self.service.change_capacity_provider(cluster_name, service_name, capacity_provider)
