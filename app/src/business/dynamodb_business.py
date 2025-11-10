from src.service.dynamodb_service import DynamoDBService
import re


class DynamoDBBusiness:
    """
    Business layer para aplicar regras de negócio nas operações com DynamoDB
    """
    
    def __init__(self):
        self.service = DynamoDBService()
    
    def validate_table_name(self, table_name):
        """
        Valida o nome da tabela conforme regras do DynamoDB
        
        Args:
            table_name (str): Nome da tabela a validar
        
        Returns:
            dict: Resultado da validação
        """
        errors = []
        
        # Verifica se o nome está vazio
        if not table_name or table_name.strip() == '':
            errors.append('O nome da tabela não pode estar vazio')
        
        # Verifica o tamanho (3-255 caracteres)
        elif len(table_name) < 3 or len(table_name) > 255:
            errors.append('O nome da tabela deve ter entre 3 e 255 caracteres')
        
        # Verifica caracteres permitidos (letras, números, underscore, hífen e ponto)
        elif not re.match(r'^[a-zA-Z0-9._-]+$', table_name):
            errors.append('O nome da tabela só pode conter letras, números, underscore (_), hífen (-) e ponto (.)')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def validate_primary_key(self, primary_key):
        """
        Valida o nome da chave primária
        
        Args:
            primary_key (str): Nome da chave primária
        
        Returns:
            dict: Resultado da validação
        """
        errors = []
        
        # Verifica se está vazio
        if not primary_key or primary_key.strip() == '':
            errors.append('O nome da chave primária não pode estar vazio')
        
        # Verifica o tamanho (1-255 caracteres)
        elif len(primary_key) < 1 or len(primary_key) > 255:
            errors.append('O nome da chave primária deve ter entre 1 e 255 caracteres')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def validate_key_type(self, key_type):
        """
        Valida o tipo da chave primária
        
        Args:
            key_type (str): Tipo da chave ('S', 'N', ou 'B')
        
        Returns:
            dict: Resultado da validação
        """
        valid_types = ['S', 'N', 'B']
        
        if key_type not in valid_types:
            return {
                'valid': False,
                'errors': [f'Tipo de chave inválido. Use: S (String), N (Number) ou B (Binary)']
            }
        
        return {
            'valid': True,
            'errors': []
        }
    
    def create_table(self, table_name, primary_key, primary_key_type='S'):
        """
        Cria uma tabela aplicando validações de negócio
        
        Args:
            table_name (str): Nome da tabela
            primary_key (str): Nome da chave primária
            primary_key_type (str): Tipo da chave primária
        
        Returns:
            dict: Resultado da operação
        """
        # Valida o nome da tabela
        table_validation = self.validate_table_name(table_name)
        if not table_validation['valid']:
            return {
                'success': False,
                'message': 'Validação falhou',
                'errors': table_validation['errors']
            }
        
        # Valida a chave primária
        key_validation = self.validate_primary_key(primary_key)
        if not key_validation['valid']:
            return {
                'success': False,
                'message': 'Validação falhou',
                'errors': key_validation['errors']
            }
        
        # Valida o tipo da chave
        type_validation = self.validate_key_type(primary_key_type)
        if not type_validation['valid']:
            return {
                'success': False,
                'message': 'Validação falhou',
                'errors': type_validation['errors']
            }
        
        # Verifica se a tabela já existe
        existing_tables = self.service.list_tables()
        if existing_tables['success'] and table_name in existing_tables['tables']:
            return {
                'success': False,
                'message': f'A tabela "{table_name}" já existe',
                'errors': ['Tabela já existe']
            }
        
        # Cria a tabela
        result = self.service.create_table(table_name, primary_key, primary_key_type)
        
        return result
    
    def list_tables(self):
        """
        Lista todas as tabelas
        
        Returns:
            dict: Lista de tabelas
        """
        return self.service.list_tables()
    
    def get_table_info(self, table_name):
        """
        Obtém informações de uma tabela
        
        Args:
            table_name (str): Nome da tabela
        
        Returns:
            dict: Informações da tabela
        """
        return self.service.describe_table(table_name)
    
    def delete_table(self, table_name):
        """
        Deleta uma tabela com validações
        
        Args:
            table_name (str): Nome da tabela
        
        Returns:
            dict: Resultado da operação
        """
        # Valida o nome da tabela
        table_validation = self.validate_table_name(table_name)
        if not table_validation['valid']:
            return {
                'success': False,
                'message': 'Validação falhou',
                'errors': table_validation['errors']
            }
        
        # Deleta a tabela
        return self.service.delete_table(table_name)
