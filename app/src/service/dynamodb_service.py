import boto3
from boto3 import Session
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

load_dotenv()

# Força o boto3 a recarregar as credenciais a cada requisição
# Isso é importante para o AWS Toolkit funcionar corretamente
boto3.setup_default_session()


class DynamoDBService:
    """
    Service layer para gerenciar conexões e operações com DynamoDB usando boto3
    """
    
    def __init__(self):
        """
        Inicializa a conexão com DynamoDB usando boto3
        
        O boto3 usa a cadeia de credenciais padrão na seguinte ordem:
        1. Parâmetros explícitos (aws_access_key_id, aws_secret_access_key)
        2. Variáveis de ambiente (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        3. Arquivo de credenciais (~/.aws/credentials)
        4. AWS Toolkit / SSO
        5. IAM Role / Container credentials
        """
        self.aws_region = os.getenv('AWS_REGION', 'sa-east-1')
        
        # Verifica se há credenciais explícitas no .env
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        # Cria uma nova sessão boto3 para garantir credenciais atualizadas
        # Isso é crucial para o AWS Toolkit funcionar corretamente
        session = Session()
        self.dynamodb_client = session.client(
                'dynamodb',
            region_name=self.aws_region
        )
            
        self.dynamodb_resource = session.resource(
            'dynamodb',
            region_name=self.aws_region
        )
    
    def create_table(self, table_name, primary_key, primary_key_type='S'):
        """
        Cria uma nova tabela no DynamoDB
        
        Args:
            table_name (str): Nome da tabela a ser criada
            primary_key (str): Nome da chave primária
            primary_key_type (str): Tipo da chave primária ('S' para String, 'N' para Number, 'B' para Binary)
        
        Returns:
            dict: Resposta da criação da tabela ou erro
        """
        try:
            response = self.dynamodb_client.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': primary_key,
                        'KeyType': 'HASH'  # Partition key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': primary_key,
                        'AttributeType': primary_key_type
                    }
                ],
                BillingMode='PAY_PER_REQUEST'  # On-demand billing
            )
            
            return {
                'success': True,
                'message': f'Tabela {table_name} criada com sucesso!',
                'data': response
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            return {
                'success': False,
                'message': f'Erro ao criar tabela: {error_message}',
                'error_code': error_code
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def list_tables(self):
        """
        Lista todas as tabelas DynamoDB
        
        Returns:
            dict: Lista de tabelas ou erro
        """
        try:
            response = self.dynamodb_client.list_tables()
            
            return {
                'success': True,
                'tables': response.get('TableNames', [])
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao listar tabelas: {e.response["Error"]["Message"]}'
            }
    
    def describe_table(self, table_name):
        """
        Obtém informações detalhadas sobre uma tabela
        
        Args:
            table_name (str): Nome da tabela
        
        Returns:
            dict: Informações da tabela ou erro
        """
        try:
            response = self.dynamodb_client.describe_table(TableName=table_name)
            
            return {
                'success': True,
                'data': response['Table']
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao descrever tabela: {e.response["Error"]["Message"]}'
            }
    
    def delete_table(self, table_name):
        """
        Deleta uma tabela do DynamoDB
        
        Args:
            table_name (str): Nome da tabela a ser deletada
        
        Returns:
            dict: Resposta da deleção ou erro
        """
        try:
            response = self.dynamodb_client.delete_table(TableName=table_name)
            
            return {
                'success': True,
                'message': f'Tabela {table_name} deletada com sucesso!',
                'data': response
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao deletar tabela: {e.response["Error"]["Message"]}'
            }
