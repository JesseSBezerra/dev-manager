from src.service.parameter_store_service import ParameterStoreService
import re


class ParameterStoreBusiness:
    """
    Business layer para Parameter Store - validações e regras de negócio
    """
    
    def __init__(self):
        """
        Inicializa a camada de negócio
        """
        self.service = ParameterStoreService()
    
    def list_all_parameters(self):
        """
        Lista todos os parâmetros com formatação
        
        Returns:
            dict: Lista formatada de parâmetros
        """
        result = self.service.list_parameters()
        
        if result['success']:
            # Formata os parâmetros
            formatted_params = []
            for param in result['parameters']:
                formatted_params.append({
                    'name': param.get('Name'),
                    'type': param.get('Type'),
                    'description': param.get('Description', 'Sem descrição'),
                    'last_modified_date': param.get('LastModifiedDate'),
                    'version': param.get('Version', 1),
                    'tier': param.get('Tier', 'Standard'),
                    'data_type': param.get('DataType', 'text')
                })
            
            return {
                'success': True,
                'parameters': formatted_params,
                'count': len(formatted_params)
            }
        
        return result
    
    def get_parameter_value(self, name):
        """
        Obtém valor de um parâmetro com validações
        
        Args:
            name (str): Nome do parâmetro
        
        Returns:
            dict: Valor do parâmetro
        """
        validation = self._validate_parameter_name(name)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        return self.service.get_parameter(name)
    
    def get_parameter_details(self, name):
        """
        Obtém detalhes completos de um parâmetro
        
        Args:
            name (str): Nome do parâmetro
        
        Returns:
            dict: Detalhes do parâmetro
        """
        validation = self._validate_parameter_name(name)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        # Obtém o parâmetro
        result = self.service.get_parameter(name)
        
        if result['success']:
            param = result['parameter']
            
            return {
                'success': True,
                'parameter': {
                    'name': param.get('Name'),
                    'value': param.get('Value'),
                    'type': param.get('Type'),
                    'version': param.get('Version'),
                    'last_modified_date': param.get('LastModifiedDate'),
                    'arn': param.get('ARN'),
                    'data_type': param.get('DataType', 'text')
                }
            }
        
        return result
    
    def get_history(self, name):
        """
        Obtém histórico de um parâmetro
        
        Args:
            name (str): Nome do parâmetro
        
        Returns:
            dict: Histórico
        """
        validation = self._validate_parameter_name(name)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        return self.service.get_parameter_history(name)
    
    def create_new_parameter(self, name, value, parameter_type, description=None):
        """
        Cria um novo parâmetro com validações
        
        Args:
            name (str): Nome do parâmetro
            value (str): Valor
            parameter_type (str): Tipo
            description (str): Descrição
        
        Returns:
            dict: Resultado
        """
        # Valida nome
        validation = self._validate_parameter_name(name)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        # Valida valor
        if not value or value.strip() == '':
            return {
                'success': False,
                'message': 'Valor do parâmetro é obrigatório'
            }
        
        # Valida tipo
        valid_types = ['String', 'StringList', 'SecureString']
        if parameter_type not in valid_types:
            return {
                'success': False,
                'message': f'Tipo inválido. Use: {", ".join(valid_types)}'
            }
        
        return self.service.create_parameter(name, value, parameter_type, description)
    
    def update_existing_parameter(self, name, value, description=None):
        """
        Atualiza um parâmetro com validações
        
        Args:
            name (str): Nome do parâmetro
            value (str): Novo valor
            description (str): Nova descrição
        
        Returns:
            dict: Resultado
        """
        validation = self._validate_parameter_name(name)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        if not value or value.strip() == '':
            return {
                'success': False,
                'message': 'Valor do parâmetro é obrigatório'
            }
        
        return self.service.update_parameter(name, value, description)
    
    def delete_parameter(self, name):
        """
        Deleta um parâmetro com validações
        
        Args:
            name (str): Nome do parâmetro
        
        Returns:
            dict: Resultado
        """
        validation = self._validate_parameter_name(name)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        return self.service.delete_parameter(name)
    
    def get_by_path(self, path):
        """
        Obtém parâmetros por caminho
        
        Args:
            path (str): Caminho
        
        Returns:
            dict: Lista de parâmetros
        """
        if not path or path.strip() == '':
            return {
                'success': False,
                'message': 'Caminho é obrigatório'
            }
        
        # Garante que começa com /
        if not path.startswith('/'):
            path = '/' + path
        
        return self.service.get_parameters_by_path(path)
    
    def _validate_parameter_name(self, name):
        """
        Valida nome do parâmetro
        
        Returns:
            dict: Resultado da validação
        """
        if not name or name.strip() == '':
            return {
                'valid': False,
                'message': 'Nome do parâmetro é obrigatório'
            }
        
        # Tamanho máximo
        if len(name) > 2048:
            return {
                'valid': False,
                'message': 'Nome muito longo (máximo 2048 caracteres)'
            }
        
        # Padrão válido: deve começar com /
        if not name.startswith('/'):
            return {
                'valid': False,
                'message': 'Nome deve começar com /'
            }
        
        # Caracteres válidos
        if not re.match(r'^[a-zA-Z0-9/_.-]+$', name):
            return {
                'valid': False,
                'message': 'Nome contém caracteres inválidos. Use apenas: a-z A-Z 0-9 / _ . -'
            }
        
        return {'valid': True}
