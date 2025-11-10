import boto3
from boto3 import Session
from botocore.exceptions import ClientError
import os
import json
from dotenv import load_dotenv

load_dotenv()


class EC2Service:
    """
    Service layer para gerenciar operações com EC2 usando boto3
    """
    
    def __init__(self):
        """
        Inicializa a conexão com EC2 usando boto3
        """
        self.aws_region = os.getenv('AWS_REGION', 'sa-east-1')
        
        session = Session()
        
        # Usa a cadeia de credenciais padrão (AWS Toolkit, CLI, etc.)
        self.ec2_client = session.client(
            'ec2',
            region_name=self.aws_region
        )
        self.ec2_resource = session.resource(
            'ec2',
            region_name=self.aws_region
        )
    
    def list_instances(self):
        """
        Lista todas as instâncias EC2
        
        Returns:
            dict: Lista de instâncias ou erro
        """
        try:
            response = self.ec2_client.describe_instances()
            
            instances = []
            for reservation in response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    instances.append(instance)
            
            return {
                'success': True,
                'instances': instances,
                'count': len(instances)
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao listar instâncias: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def get_instance(self, instance_id):
        """
        Obtém detalhes de uma instância específica
        
        Args:
            instance_id (str): ID da instância
        
        Returns:
            dict: Detalhes da instância ou erro
        """
        try:
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            
            if response['Reservations']:
                instance = response['Reservations'][0]['Instances'][0]
                return {
                    'success': True,
                    'instance': instance
                }
            else:
                return {
                    'success': False,
                    'message': 'Instância não encontrada'
                }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao obter detalhes: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def create_bastion_instance(self, name, instance_type='t3.micro', key_name=None, 
                               subnet_id=None, security_group_ids=None):
        """
        Cria uma instância EC2 configurada como Bastion Host com SSM
        
        Args:
            name (str): Nome da instância
            instance_type (str): Tipo da instância (padrão: t3.micro)
            key_name (str): Nome do key pair (opcional)
            subnet_id (str): ID da subnet (opcional)
            security_group_ids (list): IDs dos security groups (opcional)
        
        Returns:
            dict: Resultado da operação
        """
        try:
            # AMI do Amazon Linux 2 (com SSM Agent pré-instalado)
            # Busca a AMI mais recente do Amazon Linux 2
            ami_response = self.ec2_client.describe_images(
                Owners=['amazon'],
                Filters=[
                    {'Name': 'name', 'Values': ['amzn2-ami-hvm-*-x86_64-gp2']},
                    {'Name': 'state', 'Values': ['available']}
                ]
            )
            
            if not ami_response['Images']:
                return {
                    'success': False,
                    'message': 'Nenhuma AMI do Amazon Linux 2 encontrada'
                }
            
            # Ordena por data de criação e pega a mais recente
            latest_ami = sorted(ami_response['Images'], 
                              key=lambda x: x['CreationDate'], 
                              reverse=True)[0]
            ami_id = latest_ami['ImageId']
            
            # User data para configurar o bastion
            user_data = """#!/bin/bash
# Atualiza o sistema
yum update -y

# Instala ferramentas úteis
yum install -y mysql postgresql telnet nc

# Garante que o SSM Agent está rodando
systemctl enable amazon-ssm-agent
systemctl start amazon-ssm-agent

# Configura hostname
hostnamectl set-hostname bastion-host
"""
            
            # Cria ou obtém IAM Role para SSM
            iam_instance_profile = self._get_or_create_ssm_role()
            
            # Parâmetros da instância
            params = {
                'ImageId': ami_id,
                'InstanceType': instance_type,
                'MinCount': 1,
                'MaxCount': 1,
                'UserData': user_data,
                'TagSpecifications': [
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'Name', 'Value': name},
                            {'Key': 'Type', 'Value': 'Bastion'},
                            {'Key': 'ManagedBy', 'Value': 'AWSManager'}
                        ]
                    }
                ],
                'MetadataOptions': {
                    'HttpTokens': 'required',  # IMDSv2
                    'HttpPutResponseHopLimit': 1
                }
            }
            
            # Adiciona IAM Instance Profile se foi criado
            if iam_instance_profile:
                params['IamInstanceProfile'] = {'Name': iam_instance_profile}
                print(f"✅ Usando Instance Profile: {iam_instance_profile}")
            else:
                print(f"⚠️  Instância será criada SEM IAM Role")
                print(f"💡 Você precisará anexar manualmente o Instance Profile 'EC2-SSM-InstanceProfile' depois")
            
            # Adiciona key pair se fornecido
            if key_name:
                params['KeyName'] = key_name
            
            # Adiciona subnet se fornecida
            if subnet_id:
                params['SubnetId'] = subnet_id
            
            # Adiciona security groups se fornecidos
            if security_group_ids:
                params['SecurityGroupIds'] = security_group_ids
            
            response = self.ec2_client.run_instances(**params)
            instance = response['Instances'][0]
            
            return {
                'success': True,
                'message': f'Bastion Host {name} criado com sucesso',
                'instance': instance,
                'instance_id': instance['InstanceId']
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao criar instância: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def create_instance(self, name, ami_id, instance_type, key_name=None, 
                       subnet_id=None, security_group_ids=None, user_data=None):
        """
        Cria uma instância EC2 genérica
        
        Args:
            name (str): Nome da instância
            ami_id (str): ID da AMI
            instance_type (str): Tipo da instância
            key_name (str): Nome do key pair (opcional)
            subnet_id (str): ID da subnet (opcional)
            security_group_ids (list): IDs dos security groups (opcional)
            user_data (str): Script de inicialização (opcional)
        
        Returns:
            dict: Resultado da operação
        """
        try:
            params = {
                'ImageId': ami_id,
                'InstanceType': instance_type,
                'MinCount': 1,
                'MaxCount': 1,
                'TagSpecifications': [
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'Name', 'Value': name},
                            {'Key': 'ManagedBy', 'Value': 'AWSManager'}
                        ]
                    }
                ]
            }
            
            if key_name:
                params['KeyName'] = key_name
            if subnet_id:
                params['SubnetId'] = subnet_id
            if security_group_ids:
                params['SecurityGroupIds'] = security_group_ids
            if user_data:
                params['UserData'] = user_data
            
            response = self.ec2_client.run_instances(**params)
            instance = response['Instances'][0]
            
            return {
                'success': True,
                'message': f'Instância {name} criada com sucesso',
                'instance': instance,
                'instance_id': instance['InstanceId']
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao criar instância: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def start_instance(self, instance_id):
        """
        Inicia uma instância EC2
        
        Args:
            instance_id (str): ID da instância
        
        Returns:
            dict: Resultado da operação
        """
        try:
            response = self.ec2_client.start_instances(InstanceIds=[instance_id])
            
            return {
                'success': True,
                'message': f'Instância {instance_id} iniciada com sucesso',
                'state': response['StartingInstances'][0]['CurrentState']['Name']
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao iniciar instância: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def stop_instance(self, instance_id):
        """
        Para uma instância EC2
        
        Args:
            instance_id (str): ID da instância
        
        Returns:
            dict: Resultado da operação
        """
        try:
            response = self.ec2_client.stop_instances(InstanceIds=[instance_id])
            
            return {
                'success': True,
                'message': f'Instância {instance_id} parada com sucesso',
                'state': response['StoppingInstances'][0]['CurrentState']['Name']
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao parar instância: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def terminate_instance(self, instance_id):
        """
        Termina (deleta) uma instância EC2
        
        Args:
            instance_id (str): ID da instância
        
        Returns:
            dict: Resultado da operação
        """
        try:
            response = self.ec2_client.terminate_instances(InstanceIds=[instance_id])
            
            return {
                'success': True,
                'message': f'Instância {instance_id} terminada com sucesso',
                'state': response['TerminatingInstances'][0]['CurrentState']['Name']
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao terminar instância: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def get_ssm_connection_command(self, instance_id):
        """
        Gera o comando para conectar via SSM Session Manager
        
        Args:
            instance_id (str): ID da instância
        
        Returns:
            dict: Comando de conexão
        """
        return {
            'success': True,
            'command': f'aws ssm start-session --target {instance_id} --region {self.aws_region}',
            'instance_id': instance_id,
            'instructions': [
                '1. Certifique-se de ter o AWS CLI instalado',
                '2. Instale o Session Manager plugin: https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html',
                '3. Execute o comando acima no terminal',
                '4. Para criar túnel para RDS: aws ssm start-session --target {instance_id} --document-name AWS-StartPortForwardingSessionToRemoteHost --parameters host="RDS_ENDPOINT",portNumber="3306",localPortNumber="3306"'
            ]
        }
    
    def _get_or_create_ssm_role(self):
        """
        Obtém ou cria uma IAM Role para SSM
        
        Returns:
            str: Nome do instance profile ou None
        """
        import time
        
        try:
            iam_client = boto3.client('iam')
            
            role_name = 'EC2-SSM-Role'
            instance_profile_name = 'EC2-SSM-InstanceProfile'
            
            # Tenta obter o instance profile existente
            try:
                response = iam_client.get_instance_profile(InstanceProfileName=instance_profile_name)
                # Verifica se tem a role anexada
                if response['InstanceProfile'].get('Roles'):
                    print(f"✅ Instance Profile '{instance_profile_name}' já existe")
                    return instance_profile_name
            except ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchEntity':
                    raise
            
            print(f"🔧 Criando IAM Role e Instance Profile para SSM...")
            
            # Cria a role se não existir
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "ec2.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }
            
            try:
                iam_client.create_role(
                    RoleName=role_name,
                    AssumeRolePolicyDocument=json.dumps(trust_policy),
                    Description='Role for EC2 instances to use SSM Session Manager'
                )
                print(f"✅ Role '{role_name}' criada")
                
                # Aguarda a role ser criada
                time.sleep(2)
                
                # Anexa a policy gerenciada do SSM
                iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn='arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore'
                )
                print(f"✅ Policy SSM anexada à role")
                
            except ClientError as e:
                if e.response['Error']['Code'] == 'EntityAlreadyExists':
                    print(f"ℹ️  Role '{role_name}' já existe")
                else:
                    raise
            
            # Cria o instance profile
            try:
                iam_client.create_instance_profile(
                    InstanceProfileName=instance_profile_name
                )
                print(f"✅ Instance Profile '{instance_profile_name}' criado")
                
                # Aguarda o instance profile ser criado
                time.sleep(2)
                
                # Adiciona a role ao instance profile
                iam_client.add_role_to_instance_profile(
                    InstanceProfileName=instance_profile_name,
                    RoleName=role_name
                )
                print(f"✅ Role adicionada ao Instance Profile")
                
                # Aguarda propagação (importante!)
                print(f"⏳ Aguardando propagação do IAM (10 segundos)...")
                time.sleep(10)
                
            except ClientError as e:
                if e.response['Error']['Code'] == 'EntityAlreadyExists':
                    print(f"ℹ️  Instance Profile '{instance_profile_name}' já existe")
                    # Tenta adicionar a role se não estiver
                    try:
                        iam_client.add_role_to_instance_profile(
                            InstanceProfileName=instance_profile_name,
                            RoleName=role_name
                        )
                        time.sleep(5)
                    except:
                        pass
                else:
                    raise
            
            return instance_profile_name
            
        except Exception as e:
            print(f"⚠️  Aviso: Não foi possível criar IAM Role: {str(e)}")
            print(f"💡 Dica: Crie manualmente ou verifique permissões IAM")
            return None
    
    def list_available_amis(self, owner='amazon', name_filter='amzn2-ami-hvm*'):
        """
        Lista AMIs disponíveis
        
        Args:
            owner (str): Proprietário das AMIs
            name_filter (str): Filtro de nome
        
        Returns:
            dict: Lista de AMIs
        """
        try:
            response = self.ec2_client.describe_images(
                Owners=[owner],
                Filters=[
                    {'Name': 'name', 'Values': [name_filter]},
                    {'Name': 'state', 'Values': ['available']}
                ]
            )
            
            # Ordena por data de criação
            amis = sorted(response['Images'], 
                         key=lambda x: x['CreationDate'], 
                         reverse=True)[:10]  # Top 10 mais recentes
            
            return {
                'success': True,
                'amis': amis,
                'count': len(amis)
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao listar AMIs: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
