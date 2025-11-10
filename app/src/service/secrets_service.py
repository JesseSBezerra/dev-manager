import boto3
from boto3 import Session
from botocore.exceptions import ClientError
import os
import json
from dotenv import load_dotenv

load_dotenv()


class SecretsManagerService:
    """
    Service layer para gerenciar operações com AWS Secrets Manager usando boto3
    """
    
    def __init__(self):
        """
        Inicializa a conexão com Secrets Manager usando boto3
        """
        self.aws_region = os.getenv('AWS_REGION', 'sa-east-1')
        
        session = Session()
        
        # Usa a cadeia de credenciais padrão (AWS Toolkit, CLI, etc.)
        self.secrets_client = session.client(
            'secretsmanager',
            region_name=self.aws_region
        )
    
    def list_secrets(self):
        """
        Lista todos os segredos do Secrets Manager
        
        Returns:
            dict: Lista de segredos ou erro
        """
        try:
            secrets = []
            paginator = self.secrets_client.get_paginator('list_secrets')
            
            for page in paginator.paginate():
                for secret in page.get('SecretList', []):
                    secrets.append(secret)
            
            return {
                'success': True,
                'secrets': secrets,
                'count': len(secrets)
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao listar segredos: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def get_secret_value(self, secret_name):
        """
        Obtém o valor de um segredo específico
        
        Args:
            secret_name (str): Nome ou ARN do segredo
        
        Returns:
            dict: Valor do segredo ou erro
        """
        try:
            response = self.secrets_client.get_secret_value(SecretId=secret_name)
            
            # Extrai o valor do segredo
            if 'SecretString' in response:
                secret_value = response['SecretString']
                
                # Tenta parsear como JSON
                try:
                    secret_json = json.loads(secret_value)
                    is_json = True
                except json.JSONDecodeError:
                    secret_json = None
                    is_json = False
                
                return {
                    'success': True,
                    'secret_name': secret_name,
                    'secret_string': secret_value,
                    'secret_json': secret_json,
                    'is_json': is_json,
                    'version_id': response.get('VersionId'),
                    'created_date': response.get('CreatedDate').isoformat() if response.get('CreatedDate') else None
                }
            elif 'SecretBinary' in response:
                # Segredo binário
                return {
                    'success': True,
                    'secret_name': secret_name,
                    'secret_binary': response['SecretBinary'],
                    'is_binary': True,
                    'version_id': response.get('VersionId'),
                    'created_date': response.get('CreatedDate').isoformat() if response.get('CreatedDate') else None
                }
            else:
                return {
                    'success': False,
                    'message': 'Segredo não contém valor'
                }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'ResourceNotFoundException':
                return {
                    'success': False,
                    'message': f'Segredo "{secret_name}" não encontrado'
                }
            elif error_code == 'InvalidRequestException':
                return {
                    'success': False,
                    'message': 'Requisição inválida. Verifique o nome do segredo.'
                }
            elif error_code == 'InvalidParameterException':
                return {
                    'success': False,
                    'message': 'Parâmetro inválido'
                }
            else:
                return {
                    'success': False,
                    'message': f'Erro ao obter segredo: {e.response["Error"]["Message"]}'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def describe_secret(self, secret_name):
        """
        Obtém detalhes de um segredo (sem revelar o valor)
        
        Args:
            secret_name (str): Nome ou ARN do segredo
        
        Returns:
            dict: Detalhes do segredo ou erro
        """
        try:
            response = self.secrets_client.describe_secret(SecretId=secret_name)
            
            return {
                'success': True,
                'secret': response
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao descrever segredo: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def create_secret(self, name, secret_value, description=None, tags=None):
        """
        Cria um novo segredo
        
        Args:
            name (str): Nome do segredo
            secret_value (str): Valor do segredo (string ou JSON)
            description (str): Descrição do segredo (opcional)
            tags (list): Lista de tags (opcional)
        
        Returns:
            dict: Resultado da operação
        """
        try:
            params = {
                'Name': name,
                'SecretString': secret_value
            }
            
            if description:
                params['Description'] = description
            
            if tags:
                params['Tags'] = tags
            
            response = self.secrets_client.create_secret(**params)
            
            return {
                'success': True,
                'message': f'Segredo "{name}" criado com sucesso',
                'arn': response['ARN'],
                'name': response['Name'],
                'version_id': response.get('VersionId')
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'ResourceExistsException':
                return {
                    'success': False,
                    'message': f'Segredo "{name}" já existe'
                }
            elif error_code == 'InvalidRequestException':
                return {
                    'success': False,
                    'message': 'Requisição inválida. Verifique os parâmetros.'
                }
            else:
                return {
                    'success': False,
                    'message': f'Erro ao criar segredo: {e.response["Error"]["Message"]}'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def update_secret(self, secret_name, secret_value):
        """
        Atualiza o valor de um segredo existente
        
        Args:
            secret_name (str): Nome do segredo
            secret_value (str): Novo valor
        
        Returns:
            dict: Resultado da operação
        """
        try:
            response = self.secrets_client.update_secret(
                SecretId=secret_name,
                SecretString=secret_value
            )
            
            return {
                'success': True,
                'message': f'Segredo "{secret_name}" atualizado com sucesso',
                'arn': response['ARN'],
                'name': response['Name'],
                'version_id': response.get('VersionId')
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao atualizar segredo: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def delete_secret(self, secret_name, recovery_window_days=30, force_delete=False):
        """
        Deleta um segredo (com período de recuperação)
        
        Args:
            secret_name (str): Nome do segredo
            recovery_window_days (int): Dias para recuperação (7-30, padrão 30)
            force_delete (bool): Deletar imediatamente sem recuperação
        
        Returns:
            dict: Resultado da operação
        """
        try:
            params = {'SecretId': secret_name}
            
            if force_delete:
                params['ForceDeleteWithoutRecovery'] = True
            else:
                params['RecoveryWindowInDays'] = recovery_window_days
            
            response = self.secrets_client.delete_secret(**params)
            
            deletion_date = response.get('DeletionDate')
            
            if force_delete:
                message = f'Segredo "{secret_name}" deletado permanentemente'
            else:
                message = f'Segredo "{secret_name}" agendado para deleção em {recovery_window_days} dias'
            
            return {
                'success': True,
                'message': message,
                'arn': response['ARN'],
                'name': response['Name'],
                'deletion_date': deletion_date.isoformat() if deletion_date else None
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao deletar segredo: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def restore_secret(self, secret_name):
        """
        Restaura um segredo que foi agendado para deleção
        
        Args:
            secret_name (str): Nome do segredo
        
        Returns:
            dict: Resultado da operação
        """
        try:
            response = self.secrets_client.restore_secret(SecretId=secret_name)
            
            return {
                'success': True,
                'message': f'Segredo "{secret_name}" restaurado com sucesso',
                'arn': response['ARN'],
                'name': response['Name']
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao restaurar segredo: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
