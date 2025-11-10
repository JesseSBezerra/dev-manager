import boto3
from boto3 import Session
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

load_dotenv()


class RDSService:
    """
    Service layer para gerenciar operações com RDS (Relational Database Service) usando boto3
    """
    
    def __init__(self):
        """
        Inicializa a conexão com RDS usando boto3
        """
        self.aws_region = os.getenv('AWS_REGION', 'sa-east-1')
        
        session = Session()
        
        # Usa a cadeia de credenciais padrão (AWS Toolkit, CLI, etc.)
        self.rds_client = session.client(
            'rds',
            region_name=self.aws_region
        )
    
    def list_db_instances(self):
        """
        Lista todas as instâncias RDS
        
        Returns:
            dict: Lista de instâncias ou erro
        """
        try:
            response = self.rds_client.describe_db_instances()
            instances = response.get('DBInstances', [])
            
            return {
                'success': True,
                'instances': instances,
                'count': len(instances)
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao listar instâncias RDS: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def get_db_instance(self, db_instance_identifier):
        """
        Obtém detalhes de uma instância RDS específica
        
        Args:
            db_instance_identifier (str): Identificador da instância
        
        Returns:
            dict: Detalhes da instância ou erro
        """
        try:
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=db_instance_identifier
            )
            instances = response.get('DBInstances', [])
            
            if instances:
                return {
                    'success': True,
                    'instance': instances[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Instância não encontrada'
                }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao obter detalhes da instância: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def create_db_instance(self, db_instance_identifier, db_instance_class, engine, 
                          master_username, master_password, allocated_storage=20,
                          db_name=None, publicly_accessible=False, multi_az=False,
                          storage_type='gp2', backup_retention_period=7):
        """
        Cria uma nova instância RDS
        
        Args:
            db_instance_identifier (str): Identificador único da instância
            db_instance_class (str): Classe da instância (ex: db.t3.micro)
            engine (str): Engine do banco (mysql, postgres, mariadb, etc)
            master_username (str): Nome do usuário master
            master_password (str): Senha do usuário master
            allocated_storage (int): Armazenamento em GB (padrão: 20)
            db_name (str): Nome do banco de dados inicial (opcional)
            publicly_accessible (bool): Se a instância será publicamente acessível
            multi_az (bool): Se será Multi-AZ para alta disponibilidade
            storage_type (str): Tipo de armazenamento (gp2, gp3, io1)
            backup_retention_period (int): Dias de retenção de backup (0-35)
        
        Returns:
            dict: Resultado da operação
        """
        try:
            params = {
                'DBInstanceIdentifier': db_instance_identifier,
                'DBInstanceClass': db_instance_class,
                'Engine': engine,
                'MasterUsername': master_username,
                'MasterUserPassword': master_password,
                'AllocatedStorage': allocated_storage,
                'PubliclyAccessible': publicly_accessible,
                'MultiAZ': multi_az,
                'StorageType': storage_type,
                'BackupRetentionPeriod': backup_retention_period,
                'StorageEncrypted': True  # Sempre usar criptografia
            }
            
            # Adiciona nome do banco se fornecido
            if db_name:
                params['DBName'] = db_name
            
            response = self.rds_client.create_db_instance(**params)
            
            return {
                'success': True,
                'message': f'Instância RDS {db_instance_identifier} criada com sucesso',
                'instance': response.get('DBInstance', {})
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'DBInstanceAlreadyExists':
                return {
                    'success': False,
                    'message': f'Instância {db_instance_identifier} já existe'
                }
            
            return {
                'success': False,
                'message': f'Erro ao criar instância: {error_message}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def delete_db_instance(self, db_instance_identifier, skip_final_snapshot=False, 
                          final_snapshot_identifier=None):
        """
        Deleta uma instância RDS
        
        Args:
            db_instance_identifier (str): Identificador da instância
            skip_final_snapshot (bool): Se deve pular o snapshot final
            final_snapshot_identifier (str): Nome do snapshot final (se não pular)
        
        Returns:
            dict: Resultado da operação
        """
        try:
            params = {
                'DBInstanceIdentifier': db_instance_identifier,
                'SkipFinalSnapshot': skip_final_snapshot
            }
            
            if not skip_final_snapshot and final_snapshot_identifier:
                params['FinalDBSnapshotIdentifier'] = final_snapshot_identifier
            
            response = self.rds_client.delete_db_instance(**params)
            
            return {
                'success': True,
                'message': f'Instância {db_instance_identifier} deletada com sucesso',
                'instance': response.get('DBInstance', {})
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao deletar instância: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def stop_db_instance(self, db_instance_identifier):
        """
        Para uma instância RDS (economizar custos)
        
        Args:
            db_instance_identifier (str): Identificador da instância
        
        Returns:
            dict: Resultado da operação
        """
        try:
            response = self.rds_client.stop_db_instance(
                DBInstanceIdentifier=db_instance_identifier
            )
            
            return {
                'success': True,
                'message': f'Instância {db_instance_identifier} parada com sucesso',
                'instance': response.get('DBInstance', {})
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'InvalidDBInstanceState':
                return {
                    'success': False,
                    'message': 'Instância não pode ser parada no estado atual'
                }
            
            return {
                'success': False,
                'message': f'Erro ao parar instância: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def start_db_instance(self, db_instance_identifier):
        """
        Inicia uma instância RDS parada
        
        Args:
            db_instance_identifier (str): Identificador da instância
        
        Returns:
            dict: Resultado da operação
        """
        try:
            response = self.rds_client.start_db_instance(
                DBInstanceIdentifier=db_instance_identifier
            )
            
            return {
                'success': True,
                'message': f'Instância {db_instance_identifier} iniciada com sucesso',
                'instance': response.get('DBInstance', {})
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'InvalidDBInstanceState':
                return {
                    'success': False,
                    'message': 'Instância não pode ser iniciada no estado atual'
                }
            
            return {
                'success': False,
                'message': f'Erro ao iniciar instância: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
    
    def modify_db_instance(self, db_instance_identifier, db_instance_class=None, 
                          allocated_storage=None, apply_immediately=False):
        """
        Modifica uma instância RDS (alterar classe ou storage)
        
        Args:
            db_instance_identifier (str): Identificador da instância
            db_instance_class (str): Nova classe da instância (opcional)
            allocated_storage (int): Novo tamanho de storage em GB (opcional)
            apply_immediately (bool): Se deve aplicar imediatamente
        
        Returns:
            dict: Resultado da operação
        """
        try:
            params = {
                'DBInstanceIdentifier': db_instance_identifier,
                'ApplyImmediately': apply_immediately
            }
            
            if db_instance_class:
                params['DBInstanceClass'] = db_instance_class
            
            if allocated_storage:
                params['AllocatedStorage'] = allocated_storage
            
            response = self.rds_client.modify_db_instance(**params)
            
            return {
                'success': True,
                'message': f'Instância {db_instance_identifier} modificada com sucesso',
                'instance': response.get('DBInstance', {})
            }
            
        except ClientError as e:
            return {
                'success': False,
                'message': f'Erro ao modificar instância: {e.response["Error"]["Message"]}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro inesperado: {str(e)}'
            }
