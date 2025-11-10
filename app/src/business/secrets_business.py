from src.service.secrets_service import SecretsManagerService
import re
import json


class SecretsManagerBusiness:
    """
    Business layer para Secrets Manager - validações e regras de negócio
    """
    
    def __init__(self):
        """
        Inicializa a camada de negócio
        """
        self.service = SecretsManagerService()
    
    def list_all_secrets(self):
        """
        Lista todos os segredos com formatação
        
        Returns:
            dict: Lista formatada de segredos
        """
        result = self.service.list_secrets()
        
        if result['success']:
            # Formata os segredos para exibição
            formatted_secrets = []
            for secret in result['secrets']:
                formatted_secrets.append({
                    'name': secret.get('Name'),
                    'arn': secret.get('ARN'),
                    'description': secret.get('Description', 'Sem descrição'),
                    'created_date': secret.get('CreatedDate').isoformat() if secret.get('CreatedDate') else 'N/A',
                    'last_changed_date': secret.get('LastChangedDate').isoformat() if secret.get('LastChangedDate') else 'N/A',
                    'last_accessed_date': secret.get('LastAccessedDate').isoformat() if secret.get('LastAccessedDate') else 'Nunca',
                    'tags': secret.get('Tags', []),
                    'rotation_enabled': secret.get('RotationEnabled', False),
                    'deleted_date': secret.get('DeletedDate').isoformat() if secret.get('DeletedDate') else None
                })
            
            return {
                'success': True,
                'secrets': formatted_secrets,
                'count': len(formatted_secrets)
            }
        
        return result
    
    def get_secret_value(self, secret_name):
        """
        Obtém o valor de um segredo com validações
        
        Args:
            secret_name (str): Nome do segredo
        
        Returns:
            dict: Valor do segredo
        """
        # Validação
        validation = self._validate_secret_name(secret_name)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        return self.service.get_secret_value(secret_name)
    
    def describe_secret(self, secret_name):
        """
        Obtém detalhes de um segredo
        
        Args:
            secret_name (str): Nome do segredo
        
        Returns:
            dict: Detalhes do segredo
        """
        validation = self._validate_secret_name(secret_name)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        result = self.service.describe_secret(secret_name)
        
        if result['success']:
            secret = result['secret']
            
            # Formata para exibição
            formatted = {
                'name': secret.get('Name'),
                'arn': secret.get('ARN'),
                'description': secret.get('Description', 'Sem descrição'),
                'created_date': secret.get('CreatedDate').isoformat() if secret.get('CreatedDate') else 'N/A',
                'last_changed_date': secret.get('LastChangedDate').isoformat() if secret.get('LastChangedDate') else 'N/A',
                'last_accessed_date': secret.get('LastAccessedDate').isoformat() if secret.get('LastAccessedDate') else 'Nunca',
                'rotation_enabled': secret.get('RotationEnabled', False),
                'rotation_lambda_arn': secret.get('RotationLambdaARN', 'N/A'),
                'tags': secret.get('Tags', []),
                'version_ids_to_stages': secret.get('VersionIdsToStages', {})
            }
            
            return {
                'success': True,
                'secret': formatted
            }
        
        return result
    
    def create_secret(self, name, secret_value, description=None, tags=None):
        """
        Cria um novo segredo com validações
        
        Args:
            name (str): Nome do segredo
            secret_value (str): Valor do segredo
            description (str): Descrição (opcional)
            tags (list): Tags (opcional)
        
        Returns:
            dict: Resultado da operação
        """
        # Validações
        validation = self._validate_secret_name(name)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        validation = self._validate_secret_value(secret_value)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        return self.service.create_secret(name, secret_value, description, tags)
    
    def update_secret(self, secret_name, secret_value):
        """
        Atualiza um segredo com validações
        
        Args:
            secret_name (str): Nome do segredo
            secret_value (str): Novo valor
        
        Returns:
            dict: Resultado da operação
        """
        validation = self._validate_secret_name(secret_name)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        validation = self._validate_secret_value(secret_value)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        return self.service.update_secret(secret_name, secret_value)
    
    def delete_secret(self, secret_name, recovery_window_days=30, force_delete=False):
        """
        Deleta um segredo com validações
        
        Args:
            secret_name (str): Nome do segredo
            recovery_window_days (int): Dias para recuperação
            force_delete (bool): Deletar imediatamente
        
        Returns:
            dict: Resultado da operação
        """
        validation = self._validate_secret_name(secret_name)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        if not force_delete:
            if recovery_window_days < 7 or recovery_window_days > 30:
                return {
                    'success': False,
                    'message': 'Período de recuperação deve ser entre 7 e 30 dias'
                }
        
        return self.service.delete_secret(secret_name, recovery_window_days, force_delete)
    
    def restore_secret(self, secret_name):
        """
        Restaura um segredo deletado
        
        Args:
            secret_name (str): Nome do segredo
        
        Returns:
            dict: Resultado da operação
        """
        validation = self._validate_secret_name(secret_name)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        return self.service.restore_secret(secret_name)
    
    def _validate_secret_name(self, name):
        """
        Valida o nome do segredo
        
        Returns:
            dict: Resultado da validação
        """
        if not name or name.strip() == '':
            return {
                'valid': False,
                'message': 'Nome do segredo é obrigatório'
            }
        
        # Nome deve ter entre 1 e 512 caracteres
        if len(name) > 512:
            return {
                'valid': False,
                'message': 'Nome do segredo muito longo (máximo 512 caracteres)'
            }
        
        # Caracteres permitidos: alfanuméricos, /_+=.@-
        if not re.match(r'^[a-zA-Z0-9/_+=.@-]+$', name):
            return {
                'valid': False,
                'message': 'Nome contém caracteres inválidos. Use apenas: a-z A-Z 0-9 / _ + = . @ -'
            }
        
        return {'valid': True}
    
    def _validate_secret_value(self, value):
        """
        Valida o valor do segredo
        
        Returns:
            dict: Resultado da validação
        """
        if not value or value.strip() == '':
            return {
                'valid': False,
                'message': 'Valor do segredo é obrigatório'
            }
        
        # Tamanho máximo: 65536 bytes
        if len(value.encode('utf-8')) > 65536:
            return {
                'valid': False,
                'message': 'Valor do segredo muito grande (máximo 64KB)'
            }
        
        return {'valid': True}
