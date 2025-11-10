from src.service.rds_service import RDSService
import re


class RDSBusiness:
    """
    Business layer para RDS - contém validações e regras de negócio
    """
    
    def __init__(self):
        """
        Inicializa a camada de negócio com o service layer
        """
        self.service = RDSService()
    
    def list_all_instances(self):
        """
        Lista todas as instâncias RDS com formatação
        
        Returns:
            dict: Lista formatada de instâncias
        """
        result = self.service.list_db_instances()
        
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
    
    def get_instance_details(self, db_instance_identifier):
        """
        Obtém detalhes de uma instância com validação
        
        Args:
            db_instance_identifier (str): Identificador da instância
        
        Returns:
            dict: Detalhes da instância
        """
        if not db_instance_identifier or db_instance_identifier.strip() == '':
            return {
                'success': False,
                'message': 'Identificador da instância é obrigatório'
            }
        
        result = self.service.get_db_instance(db_instance_identifier)
        
        if result['success']:
            result['instance'] = self._format_instance(result['instance'])
        
        return result
    
    def create_instance(self, db_instance_identifier, db_instance_class, engine,
                       master_username, master_password, allocated_storage=20,
                       db_name=None, publicly_accessible=False, multi_az=False):
        """
        Cria uma instância RDS com validações
        
        Args:
            db_instance_identifier (str): Identificador único
            db_instance_class (str): Classe da instância
            engine (str): Engine do banco
            master_username (str): Usuário master
            master_password (str): Senha master
            allocated_storage (int): Storage em GB
            db_name (str): Nome do banco inicial
            publicly_accessible (bool): Acesso público
            multi_az (bool): Multi-AZ
        
        Returns:
            dict: Resultado da operação
        """
        # Validação do identificador
        validation = self._validate_db_identifier(db_instance_identifier)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message'],
                'errors': validation['errors']
            }
        
        # Validação da classe
        validation = self._validate_instance_class(db_instance_class)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message'],
                'errors': validation['errors']
            }
        
        # Validação do engine
        validation = self._validate_engine(engine)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message'],
                'errors': validation['errors']
            }
        
        # Validação do username
        validation = self._validate_master_username(master_username, engine)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message'],
                'errors': validation['errors']
            }
        
        # Validação da senha
        validation = self._validate_master_password(master_password)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message'],
                'errors': validation['errors']
            }
        
        # Validação do storage
        validation = self._validate_allocated_storage(allocated_storage, engine)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message'],
                'errors': validation['errors']
            }
        
        # Validação do nome do banco (se fornecido)
        if db_name:
            validation = self._validate_db_name(db_name, engine)
            if not validation['valid']:
                return {
                    'success': False,
                    'message': validation['message'],
                    'errors': validation['errors']
                }
        
        return self.service.create_db_instance(
            db_instance_identifier=db_instance_identifier,
            db_instance_class=db_instance_class,
            engine=engine,
            master_username=master_username,
            master_password=master_password,
            allocated_storage=allocated_storage,
            db_name=db_name,
            publicly_accessible=publicly_accessible,
            multi_az=multi_az
        )
    
    def delete_instance(self, db_instance_identifier, skip_final_snapshot=False):
        """
        Deleta uma instância com validação
        
        Args:
            db_instance_identifier (str): Identificador da instância
            skip_final_snapshot (bool): Pular snapshot final
        
        Returns:
            dict: Resultado da operação
        """
        if not db_instance_identifier or db_instance_identifier.strip() == '':
            return {
                'success': False,
                'message': 'Identificador da instância é obrigatório'
            }
        
        # Se não pular snapshot, gera um nome automático
        final_snapshot_id = None
        if not skip_final_snapshot:
            import datetime
            timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            final_snapshot_id = f"{db_instance_identifier}-final-{timestamp}"
        
        return self.service.delete_db_instance(
            db_instance_identifier=db_instance_identifier,
            skip_final_snapshot=skip_final_snapshot,
            final_snapshot_identifier=final_snapshot_id
        )
    
    def stop_instance(self, db_instance_identifier):
        """
        Para uma instância com validação
        
        Args:
            db_instance_identifier (str): Identificador da instância
        
        Returns:
            dict: Resultado da operação
        """
        if not db_instance_identifier or db_instance_identifier.strip() == '':
            return {
                'success': False,
                'message': 'Identificador da instância é obrigatório'
            }
        
        return self.service.stop_db_instance(db_instance_identifier)
    
    def start_instance(self, db_instance_identifier):
        """
        Inicia uma instância com validação
        
        Args:
            db_instance_identifier (str): Identificador da instância
        
        Returns:
            dict: Resultado da operação
        """
        if not db_instance_identifier or db_instance_identifier.strip() == '':
            return {
                'success': False,
                'message': 'Identificador da instância é obrigatório'
            }
        
        return self.service.start_db_instance(db_instance_identifier)
    
    def _format_instance(self, instance):
        """
        Formata uma instância para exibição
        
        Args:
            instance (dict): Dados brutos da instância
        
        Returns:
            dict: Instância formatada
        """
        return {
            'identifier': instance.get('DBInstanceIdentifier', 'N/A'),
            'status': instance.get('DBInstanceStatus', 'N/A'),
            'engine': instance.get('Engine', 'N/A'),
            'engine_version': instance.get('EngineVersion', 'N/A'),
            'instance_class': instance.get('DBInstanceClass', 'N/A'),
            'storage': instance.get('AllocatedStorage', 0),
            'storage_type': instance.get('StorageType', 'N/A'),
            'multi_az': instance.get('MultiAZ', False),
            'publicly_accessible': instance.get('PubliclyAccessible', False),
            'endpoint': instance.get('Endpoint', {}).get('Address', 'N/A') if instance.get('Endpoint') else 'N/A',
            'port': instance.get('Endpoint', {}).get('Port', 'N/A') if instance.get('Endpoint') else 'N/A',
            'master_username': instance.get('MasterUsername', 'N/A'),
            'db_name': instance.get('DBName', 'N/A'),
            'backup_retention': instance.get('BackupRetentionPeriod', 0),
            'created_time': instance.get('InstanceCreateTime', 'N/A')
        }
    
    def _validate_db_identifier(self, identifier):
        """Valida o identificador da instância"""
        if not identifier or identifier.strip() == '':
            return {
                'valid': False,
                'message': 'Identificador é obrigatório',
                'errors': ['Identificador não pode estar vazio']
            }
        
        if len(identifier) < 1 or len(identifier) > 63:
            return {
                'valid': False,
                'message': 'Identificador deve ter entre 1 e 63 caracteres',
                'errors': ['Tamanho inválido']
            }
        
        if not re.match(r'^[a-z][a-z0-9-]*$', identifier):
            return {
                'valid': False,
                'message': 'Identificador deve começar com letra minúscula e conter apenas letras, números e hífens',
                'errors': ['Formato inválido']
            }
        
        if identifier.endswith('-'):
            return {
                'valid': False,
                'message': 'Identificador não pode terminar com hífen',
                'errors': ['Formato inválido']
            }
        
        return {'valid': True}
    
    def _validate_instance_class(self, instance_class):
        """Valida a classe da instância"""
        valid_classes = [
            'db.t3.micro', 'db.t3.small', 'db.t3.medium', 'db.t3.large',
            'db.t4g.micro', 'db.t4g.small', 'db.t4g.medium',
            'db.m5.large', 'db.m5.xlarge', 'db.m5.2xlarge',
            'db.r5.large', 'db.r5.xlarge', 'db.r5.2xlarge'
        ]
        
        if instance_class not in valid_classes:
            return {
                'valid': False,
                'message': f'Classe de instância inválida. Use uma das: {", ".join(valid_classes[:5])}...',
                'errors': ['Classe inválida']
            }
        
        return {'valid': True}
    
    def _validate_engine(self, engine):
        """Valida o engine do banco"""
        valid_engines = ['mysql', 'postgres', 'mariadb', 'oracle-se2', 'sqlserver-ex']
        
        if engine not in valid_engines:
            return {
                'valid': False,
                'message': f'Engine inválido. Use: {", ".join(valid_engines)}',
                'errors': ['Engine inválido']
            }
        
        return {'valid': True}
    
    def _validate_master_username(self, username, engine):
        """Valida o nome do usuário master"""
        if not username or len(username) < 1 or len(username) > 16:
            return {
                'valid': False,
                'message': 'Username deve ter entre 1 e 16 caracteres',
                'errors': ['Tamanho inválido']
            }
        
        # Palavras reservadas por engine
        reserved_words = {
            'mysql': ['admin', 'root'],
            'postgres': ['postgres', 'admin'],
            'mariadb': ['admin', 'root']
        }
        
        if engine in reserved_words and username.lower() in reserved_words[engine]:
            return {
                'valid': False,
                'message': f'Username "{username}" é reservado para {engine}',
                'errors': ['Username reservado']
            }
        
        return {'valid': True}
    
    def _validate_master_password(self, password):
        """Valida a senha master"""
        if not password or len(password) < 8:
            return {
                'valid': False,
                'message': 'Senha deve ter no mínimo 8 caracteres',
                'errors': ['Senha muito curta']
            }
        
        if len(password) > 41:
            return {
                'valid': False,
                'message': 'Senha deve ter no máximo 41 caracteres',
                'errors': ['Senha muito longa']
            }
        
        return {'valid': True}
    
    def _validate_allocated_storage(self, storage, engine):
        """Valida o armazenamento alocado"""
        min_storage = {
            'mysql': 20,
            'postgres': 20,
            'mariadb': 20,
            'oracle-se2': 20,
            'sqlserver-ex': 20
        }
        
        min_size = min_storage.get(engine, 20)
        
        if storage < min_size:
            return {
                'valid': False,
                'message': f'Storage mínimo para {engine} é {min_size} GB',
                'errors': ['Storage insuficiente']
            }
        
        if storage > 65536:
            return {
                'valid': False,
                'message': 'Storage máximo é 65536 GB (64 TB)',
                'errors': ['Storage muito grande']
            }
        
        return {'valid': True}
    
    def _validate_db_name(self, db_name, engine):
        """Valida o nome do banco de dados"""
        if not db_name:
            return {'valid': True}  # Nome do banco é opcional
        
        if len(db_name) < 1 or len(db_name) > 64:
            return {
                'valid': False,
                'message': 'Nome do banco deve ter entre 1 e 64 caracteres',
                'errors': ['Tamanho inválido']
            }
        
        if engine in ['mysql', 'mariadb']:
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', db_name):
                return {
                    'valid': False,
                    'message': 'Nome do banco deve começar com letra e conter apenas letras, números e underscore',
                    'errors': ['Formato inválido']
                }
        
        return {'valid': True}
