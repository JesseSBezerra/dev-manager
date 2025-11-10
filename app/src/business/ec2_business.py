from src.service.ec2_service import EC2Service
import re


class EC2Business:
    """
    Business layer para EC2 - contém validações e regras de negócio
    """
    
    def __init__(self):
        """
        Inicializa a camada de negócio com o service layer
        """
        self.service = EC2Service()
    
    def list_all_instances(self):
        """
        Lista todas as instâncias EC2 com formatação
        
        Returns:
            dict: Lista formatada de instâncias
        """
        result = self.service.list_instances()
        
        if not result['success']:
            return result
        
        # Formata as instâncias para exibição
        formatted_instances = []
        for instance in result['instances']:
            formatted_instances.append(self._format_instance(instance))
        
        return {
            'success': True,
            'instances': formatted_instances,
            'count': len(formatted_instances)
        }
    
    def get_instance_details(self, instance_id):
        """
        Obtém detalhes de uma instância com validação
        
        Args:
            instance_id (str): ID da instância
        
        Returns:
            dict: Detalhes da instância
        """
        if not instance_id or instance_id.strip() == '':
            return {
                'success': False,
                'message': 'ID da instância é obrigatório'
            }
        
        result = self.service.get_instance(instance_id)
        
        if result['success']:
            result['instance'] = self._format_instance(result['instance'])
        
        return result
    
    def create_bastion_host(self, name, instance_type='t3.micro', key_name=None,
                           subnet_id=None, security_group_ids=None):
        """
        Cria um Bastion Host com validações
        
        Args:
            name (str): Nome da instância
            instance_type (str): Tipo da instância
            key_name (str): Nome do key pair
            subnet_id (str): ID da subnet
            security_group_ids (list): IDs dos security groups
        
        Returns:
            dict: Resultado da operação
        """
        # Validação do nome
        if not name or name.strip() == '':
            return {
                'success': False,
                'message': 'Nome da instância é obrigatório',
                'errors': ['Nome não pode estar vazio']
            }
        
        if len(name) > 255:
            return {
                'success': False,
                'message': 'Nome muito longo (máximo 255 caracteres)',
                'errors': ['Nome inválido']
            }
        
        # Validação do tipo de instância
        valid_types = [
            't3.micro', 't3.small', 't3.medium', 't3.large',
            't2.micro', 't2.small', 't2.medium',
            't4g.micro', 't4g.small', 't4g.medium'
        ]
        
        if instance_type not in valid_types:
            return {
                'success': False,
                'message': f'Tipo de instância inválido. Use: {", ".join(valid_types[:5])}...',
                'errors': ['Tipo inválido']
            }
        
        return self.service.create_bastion_instance(
            name=name,
            instance_type=instance_type,
            key_name=key_name,
            subnet_id=subnet_id,
            security_group_ids=security_group_ids
        )
    
    def create_instance(self, name, ami_id, instance_type, key_name=None,
                       subnet_id=None, security_group_ids=None, user_data=None):
        """
        Cria uma instância EC2 com validações
        
        Args:
            name (str): Nome da instância
            ami_id (str): ID da AMI
            instance_type (str): Tipo da instância
            key_name (str): Nome do key pair
            subnet_id (str): ID da subnet
            security_group_ids (list): IDs dos security groups
            user_data (str): Script de inicialização
        
        Returns:
            dict: Resultado da operação
        """
        # Validações
        if not name or name.strip() == '':
            return {
                'success': False,
                'message': 'Nome da instância é obrigatório'
            }
        
        if not ami_id or not ami_id.startswith('ami-'):
            return {
                'success': False,
                'message': 'AMI ID inválido (deve começar com ami-)'
            }
        
        if not instance_type:
            return {
                'success': False,
                'message': 'Tipo de instância é obrigatório'
            }
        
        return self.service.create_instance(
            name=name,
            ami_id=ami_id,
            instance_type=instance_type,
            key_name=key_name,
            subnet_id=subnet_id,
            security_group_ids=security_group_ids,
            user_data=user_data
        )
    
    def start_instance(self, instance_id):
        """
        Inicia uma instância com validação
        
        Args:
            instance_id (str): ID da instância
        
        Returns:
            dict: Resultado da operação
        """
        if not instance_id or not instance_id.startswith('i-'):
            return {
                'success': False,
                'message': 'ID da instância inválido'
            }
        
        return self.service.start_instance(instance_id)
    
    def stop_instance(self, instance_id):
        """
        Para uma instância com validação
        
        Args:
            instance_id (str): ID da instância
        
        Returns:
            dict: Resultado da operação
        """
        if not instance_id or not instance_id.startswith('i-'):
            return {
                'success': False,
                'message': 'ID da instância inválido'
            }
        
        return self.service.stop_instance(instance_id)
    
    def terminate_instance(self, instance_id):
        """
        Termina uma instância com validação
        
        Args:
            instance_id (str): ID da instância
        
        Returns:
            dict: Resultado da operação
        """
        if not instance_id or not instance_id.startswith('i-'):
            return {
                'success': False,
                'message': 'ID da instância inválido'
            }
        
        return self.service.terminate_instance(instance_id)
    
    def get_ssm_connection_info(self, instance_id):
        """
        Obtém informações de conexão SSM
        
        Args:
            instance_id (str): ID da instância
        
        Returns:
            dict: Informações de conexão
        """
        if not instance_id or not instance_id.startswith('i-'):
            return {
                'success': False,
                'message': 'ID da instância inválido'
            }
        
        return self.service.get_ssm_connection_command(instance_id)
    
    def list_available_amis(self):
        """
        Lista AMIs disponíveis
        
        Returns:
            dict: Lista de AMIs formatadas
        """
        result = self.service.list_available_amis()
        
        if not result['success']:
            return result
        
        # Formata as AMIs
        formatted_amis = []
        for ami in result['amis']:
            formatted_amis.append({
                'ami_id': ami.get('ImageId', 'N/A'),
                'name': ami.get('Name', 'N/A'),
                'description': ami.get('Description', 'N/A'),
                'creation_date': ami.get('CreationDate', 'N/A'),
                'architecture': ami.get('Architecture', 'N/A'),
                'virtualization_type': ami.get('VirtualizationType', 'N/A')
            })
        
        return {
            'success': True,
            'amis': formatted_amis,
            'count': len(formatted_amis)
        }
    
    def _format_instance(self, instance):
        """
        Formata uma instância para exibição
        
        Args:
            instance (dict): Dados brutos da instância
        
        Returns:
            dict: Instância formatada
        """
        # Extrai o nome das tags
        name = 'N/A'
        tags = instance.get('Tags', [])
        for tag in tags:
            if tag['Key'] == 'Name':
                name = tag['Value']
                break
        
        # Extrai tipo (Bastion ou Normal)
        instance_type_tag = 'Normal'
        for tag in tags:
            if tag['Key'] == 'Type':
                instance_type_tag = tag['Value']
                break
        
        return {
            'instance_id': instance.get('InstanceId', 'N/A'),
            'name': name,
            'state': instance.get('State', {}).get('Name', 'N/A'),
            'instance_type': instance.get('InstanceType', 'N/A'),
            'type_tag': instance_type_tag,
            'ami_id': instance.get('ImageId', 'N/A'),
            'public_ip': instance.get('PublicIpAddress', 'N/A'),
            'private_ip': instance.get('PrivateIpAddress', 'N/A'),
            'subnet_id': instance.get('SubnetId', 'N/A'),
            'vpc_id': instance.get('VpcId', 'N/A'),
            'key_name': instance.get('KeyName', 'N/A'),
            'launch_time': instance.get('LaunchTime', 'N/A'),
            'availability_zone': instance.get('Placement', {}).get('AvailabilityZone', 'N/A'),
            'security_groups': [sg['GroupName'] for sg in instance.get('SecurityGroups', [])],
            'iam_instance_profile': instance.get('IamInstanceProfile', {}).get('Arn', 'N/A') if instance.get('IamInstanceProfile') else 'N/A'
        }
