from src.service.db_query_service import DatabaseQueryService
import re


class DatabaseQueryBusiness:
    """
    Business layer para Database Query - validações e regras de negócio
    """
    
    def __init__(self):
        """
        Inicializa a camada de negócio
        """
        self.service = DatabaseQueryService()
    
    def execute_query(self, engine, host, port, database, username, password, query):
        """
        Executa uma query com validações
        
        Args:
            engine (str): Tipo do banco (mysql, postgres, mariadb)
            host (str): Host
            port (int): Porta
            database (str): Nome do banco
            username (str): Usuário
            password (str): Senha
            query (str): Query SQL
        
        Returns:
            dict: Resultados ou erro
        """
        # Validações
        validation = self._validate_connection_params(engine, host, port, database, username, password)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        validation = self._validate_query(query)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        # Executa a query
        if engine in ['mysql', 'mariadb']:
            return self.service.execute_query_mysql(host, port, database, username, password, query)
        elif engine == 'postgres':
            return self.service.execute_query_postgresql(host, port, database, username, password, query)
        else:
            return {
                'success': False,
                'message': f'Engine não suportado: {engine}'
            }
    
    def test_connection(self, engine, host, port, database, username, password):
        """
        Testa conexão com validações
        
        Args:
            engine (str): Tipo do banco
            host (str): Host
            port (int): Porta
            database (str): Nome do banco
            username (str): Usuário
            password (str): Senha
        
        Returns:
            dict: Resultado do teste
        """
        validation = self._validate_connection_params(engine, host, port, database, username, password)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        return self.service.test_connection(engine, host, port, database, username, password)
    
    def get_tables(self, engine, host, port, database, username, password):
        """
        Lista tabelas com validações
        
        Args:
            engine (str): Tipo do banco
            host (str): Host
            port (int): Porta
            database (str): Nome do banco
            username (str): Usuário
            password (str): Senha
        
        Returns:
            dict: Lista de tabelas
        """
        validation = self._validate_connection_params(engine, host, port, database, username, password)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message']
            }
        
        return self.service.get_tables(engine, host, port, database, username, password)
    
    def create_tunnel(self, bastion_instance_id, rds_endpoint, rds_port, local_port=None):
        """
        Cria túnel SSM com validações
        
        Args:
            bastion_instance_id (str): ID do Bastion
            rds_endpoint (str): Endpoint do RDS
            rds_port (int): Porta do RDS
            local_port (int): Porta local (opcional)
        
        Returns:
            dict: Informações do túnel
        """
        # Validações
        if not bastion_instance_id or not bastion_instance_id.startswith('i-'):
            return {
                'success': False,
                'message': 'ID do Bastion inválido'
            }
        
        if not rds_endpoint or rds_endpoint.strip() == '':
            return {
                'success': False,
                'message': 'Endpoint do RDS é obrigatório'
            }
        
        if not isinstance(rds_port, int) or rds_port < 1 or rds_port > 65535:
            return {
                'success': False,
                'message': 'Porta do RDS inválida (1-65535)'
            }
        
        return self.service.create_ssm_tunnel(bastion_instance_id, rds_endpoint, rds_port, local_port)
    
    def close_tunnel(self, tunnel_key):
        """
        Fecha túnel SSM
        
        Args:
            tunnel_key (str): Chave do túnel
        
        Returns:
            dict: Resultado
        """
        if not tunnel_key:
            return {
                'success': False,
                'message': 'Chave do túnel é obrigatória'
            }
        
        return self.service.close_ssm_tunnel(tunnel_key)
    
    def _validate_connection_params(self, engine, host, port, database, username, password):
        """
        Valida parâmetros de conexão
        
        Returns:
            dict: Resultado da validação
        """
        if not engine or engine not in ['mysql', 'postgres', 'mariadb']:
            return {
                'valid': False,
                'message': 'Engine inválido. Use: mysql, postgres ou mariadb'
            }
        
        if not host or host.strip() == '':
            return {
                'valid': False,
                'message': 'Host é obrigatório'
            }
        
        if not isinstance(port, int) or port < 1 or port > 65535:
            return {
                'valid': False,
                'message': 'Porta inválida (1-65535)'
            }
        
        if not database or database.strip() == '':
            return {
                'valid': False,
                'message': 'Nome do banco é obrigatório'
            }
        
        if not username or username.strip() == '':
            return {
                'valid': False,
                'message': 'Usuário é obrigatório'
            }
        
        if not password:
            return {
                'valid': False,
                'message': 'Senha é obrigatória'
            }
        
        return {'valid': True}
    
    def _validate_query(self, query):
        """
        Valida a query SQL
        
        Returns:
            dict: Resultado da validação
        """
        if not query or query.strip() == '':
            return {
                'valid': False,
                'message': 'Query não pode estar vazia'
            }
        
        # Remove comentários e espaços
        clean_query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        clean_query = re.sub(r'/\*.*?\*/', '', clean_query, flags=re.DOTALL)
        clean_query = clean_query.strip()
        
        if not clean_query:
            return {
                'valid': False,
                'message': 'Query não pode conter apenas comentários'
            }
        
        # Verifica comandos perigosos (opcional - pode ser removido se confiar nos usuários)
        dangerous_keywords = ['DROP DATABASE', 'DROP SCHEMA']
        upper_query = clean_query.upper()
        
        for keyword in dangerous_keywords:
            if keyword in upper_query:
                return {
                    'valid': False,
                    'message': f'Comando perigoso detectado: {keyword}. Use com cuidado!'
                }
        
        # Limite de tamanho
        if len(query) > 50000:  # 50KB
            return {
                'valid': False,
                'message': 'Query muito longa (máximo 50KB)'
            }
        
        return {'valid': True}
