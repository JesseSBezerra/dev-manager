import boto3
from boto3 import Session
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

load_dotenv()


class ParameterStoreService:
    """
    Service layer para gerenciar operações com AWS Systems Manager Parameter Store usando boto3
    """
    
    def __init__(self):
        """
        Inicializa a conexão com SSM Parameter Store usando boto3
        """
        self.aws_region = os.getenv('AWS_REGION', 'sa-east-1')
        
        session = Session()
        
        # Usa a cadeia de credenciais padrão (AWS Toolkit, CLI, etc.)
        self.ssm_client = session.client(
            'ssm',
            region_name=self.aws_region
        )
    
    def list_parameters(self, max_results=50):
        """
        Lista todos os parâmetros
        
        Args:
            max_results (int): Número máximo de resultados
        
        Returns:
            dict: Lista de parâmetros ou erro
        """
        try:
            parameters = []
            next_token = None
            
            while True:
                params = {
                    'MaxResults': max_results
                }
                
                if next_token:
                    params['NextToken'] = next_token
                
                response = self.ssm_client.describe_parameters(**params)
                
                parameters.extend(response.get('Parameters', []))
                
                next_token = response.get('NextToken')
                if not next_token:
                    break
            
            return {
                'success': True,
                'parameters': parameters,
                'count': len(parameters)
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao listar parâmetros: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def get_parameter(self, name, with_decryption=True):
        """
        Obtém o valor de um parâmetro
        
        Args:
            name (str): Nome do parâmetro
            with_decryption (bool): Descriptografar valores SecureString
        
        Returns:
            dict: Valor do parâmetro ou erro
        """
        try:
            response = self.ssm_client.get_parameter(
                Name=name,
                WithDecryption=with_decryption
            )
            
            return {
                'success': True,
                'parameter': response['Parameter']
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao obter parâmetro: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def get_parameter_history(self, name, max_results=10):
        """
        Obtém histórico de um parâmetro
        
        Args:
            name (str): Nome do parâmetro
            max_results (int): Número máximo de resultados
        
        Returns:
            dict: Histórico do parâmetro ou erro
        """
        try:
            response = self.ssm_client.get_parameter_history(
                Name=name,
                MaxResults=max_results,
                WithDecryption=True
            )
            
            return {
                'success': True,
                'history': response.get('Parameters', [])
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao obter histórico: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def create_parameter(self, name, value, parameter_type='String', description=None, tags=None):
        """
        Cria um novo parâmetro
        
        Args:
            name (str): Nome do parâmetro
            value (str): Valor do parâmetro
            parameter_type (str): Tipo (String, StringList, SecureString)
            description (str): Descrição (opcional)
            tags (list): Tags (opcional)
        
        Returns:
            dict: Resultado da operação
        """
        try:
            params = {
                'Name': name,
                'Value': value,
                'Type': parameter_type,
                'Overwrite': False
            }
            
            if description:
                params['Description'] = description
            
            if tags:
                params['Tags'] = tags
            
            response = self.ssm_client.put_parameter(**params)
            
            return {
                'success': True,
                'message': f'Parâmetro "{name}" criado com sucesso',
                'version': response.get('Version')
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao criar parâmetro: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def update_parameter(self, name, value, description=None):
        """
        Atualiza um parâmetro existente
        
        Args:
            name (str): Nome do parâmetro
            value (str): Novo valor
            description (str): Nova descrição (opcional)
        
        Returns:
            dict: Resultado da operação
        """
        try:
            params = {
                'Name': name,
                'Value': value,
                'Overwrite': True
            }
            
            if description:
                params['Description'] = description
            
            response = self.ssm_client.put_parameter(**params)
            
            return {
                'success': True,
                'message': f'Parâmetro "{name}" atualizado com sucesso',
                'version': response.get('Version')
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao atualizar parâmetro: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def delete_parameter(self, name):
        """
        Deleta um parâmetro
        
        Args:
            name (str): Nome do parâmetro
        
        Returns:
            dict: Resultado da operação
        """
        try:
            self.ssm_client.delete_parameter(Name=name)
            
            return {
                'success': True,
                'message': f'Parâmetro "{name}" deletado com sucesso'
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao deletar parâmetro: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def get_parameters_by_path(self, path, recursive=True, with_decryption=True):
        """
        Obtém parâmetros por caminho
        
        Args:
            path (str): Caminho (ex: /app/prod/)
            recursive (bool): Buscar recursivamente
            with_decryption (bool): Descriptografar
        
        Returns:
            dict: Lista de parâmetros ou erro
        """
        try:
            parameters = []
            next_token = None
            
            while True:
                params = {
                    'Path': path,
                    'Recursive': recursive,
                    'WithDecryption': with_decryption,
                    'MaxResults': 10
                }
                
                if next_token:
                    params['NextToken'] = next_token
                
                response = self.ssm_client.get_parameters_by_path(**params)
                
                parameters.extend(response.get('Parameters', []))
                
                next_token = response.get('NextToken')
                if not next_token:
                    break
            
            return {
                'success': True,
                'parameters': parameters,
                'count': len(parameters)
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao buscar por caminho: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def add_tags(self, name, tags):
        """
        Adiciona tags a um parâmetro
        
        Args:
            name (str): Nome do parâmetro
            tags (list): Lista de tags
        
        Returns:
            dict: Resultado da operação
        """
        try:
            self.ssm_client.add_tags_to_resource(
                ResourceType='Parameter',
                ResourceId=name,
                Tags=tags
            )
            
            return {
                'success': True,
                'message': 'Tags adicionadas com sucesso'
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao adicionar tags: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
