import pymysql
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import subprocess
import time
import os
import signal


class DatabaseQueryService:
    """
    Service layer para executar queries em bancos de dados RDS via Bastion/SSM
    """
    
    def __init__(self):
        """
        Inicializa o serviço de queries
        """
        self.active_tunnels = {}  # Armazena processos de túnel ativos
    
    def create_ssm_tunnel(self, bastion_instance_id, rds_endpoint, rds_port, local_port=None):
        """
        Cria um túnel SSM para o RDS através do Bastion
        
        Args:
            bastion_instance_id (str): ID da instância Bastion
            rds_endpoint (str): Endpoint do RDS
            rds_port (int): Porta do RDS (3306, 5432, etc)
            local_port (int): Porta local (opcional, usa a mesma do RDS)
        
        Returns:
            dict: Informações do túnel ou erro
        """
        try:
            if local_port is None:
                local_port = rds_port
            
            # Comando SSM para port forwarding
            command = [
                'aws', 'ssm', 'start-session',
                '--target', bastion_instance_id,
                '--document-name', 'AWS-StartPortForwardingSessionToRemoteHost',
                '--parameters', f'host="{rds_endpoint}",portNumber="{rds_port}",localPortNumber="{local_port}"'
            ]
            
            # Inicia o processo em background
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            # Aguarda um pouco para o túnel estabelecer
            time.sleep(3)
            
            # Verifica se o processo ainda está rodando
            if process.poll() is not None:
                stderr = process.stderr.read().decode('utf-8')
                return {
                    'success': False,
                    'message': f'Falha ao criar túnel SSM: {stderr}'
                }
            
            # Armazena o processo
            tunnel_key = f"{bastion_instance_id}:{local_port}"
            self.active_tunnels[tunnel_key] = process
            
            return {
                'success': True,
                'message': 'Túnel SSM criado com sucesso',
                'local_port': local_port,
                'tunnel_key': tunnel_key,
                'process_id': process.pid
            }
            
        except FileNotFoundError:
            return {
                'success': False,
                'message': 'AWS CLI não encontrado. Instale o AWS CLI e o Session Manager plugin.'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao criar túnel: {str(e)}'
            }
    
    def close_ssm_tunnel(self, tunnel_key):
        """
        Fecha um túnel SSM ativo
        
        Args:
            tunnel_key (str): Chave do túnel (bastion_id:local_port)
        
        Returns:
            dict: Resultado da operação
        """
        try:
            if tunnel_key not in self.active_tunnels:
                return {
                    'success': False,
                    'message': 'Túnel não encontrado'
                }
            
            process = self.active_tunnels[tunnel_key]
            
            # Termina o processo
            if os.name == 'nt':  # Windows
                os.kill(process.pid, signal.CTRL_BREAK_EVENT)
            else:  # Linux/Mac
                process.terminate()
            
            process.wait(timeout=5)
            del self.active_tunnels[tunnel_key]
            
            return {
                'success': True,
                'message': 'Túnel fechado com sucesso'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao fechar túnel: {str(e)}'
            }
    
    def execute_query_mysql(self, host, port, database, username, password, query):
        """
        Executa uma query em MySQL/MariaDB
        
        Args:
            host (str): Host (geralmente localhost quando via túnel)
            port (int): Porta
            database (str): Nome do banco
            username (str): Usuário
            password (str): Senha
            query (str): Query SQL
        
        Returns:
            dict: Resultados ou erro
        """
        connection = None
        try:
            # Conecta ao MySQL
            connection = pymysql.connect(
                host=host,
                port=port,
                user=username,
                password=password,
                database=database,
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=10
            )
            
            with connection.cursor() as cursor:
                # Executa a query
                cursor.execute(query)
                
                # Verifica se é SELECT (retorna dados)
                if query.strip().upper().startswith('SELECT') or \
                   query.strip().upper().startswith('SHOW') or \
                   query.strip().upper().startswith('DESCRIBE'):
                    results = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    
                    return {
                        'success': True,
                        'type': 'select',
                        'columns': columns,
                        'rows': results,
                        'row_count': len(results)
                    }
                else:
                    # INSERT, UPDATE, DELETE, etc
                    connection.commit()
                    return {
                        'success': True,
                        'type': 'modify',
                        'affected_rows': cursor.rowcount,
                        'message': f'{cursor.rowcount} linha(s) afetada(s)'
                    }
            
        except pymysql.Error as e:
            return {
                'success': False,
                'message': f'Erro MySQL: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao executar query: {str(e)}'
            }
        finally:
            if connection:
                connection.close()
    
    def execute_query_postgresql(self, host, port, database, username, password, query):
        """
        Executa uma query em PostgreSQL
        
        Args:
            host (str): Host
            port (int): Porta
            database (str): Nome do banco
            username (str): Usuário
            password (str): Senha
            query (str): Query SQL
        
        Returns:
            dict: Resultados ou erro
        """
        connection = None
        try:
            # Conecta ao PostgreSQL
            connection = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password,
                connect_timeout=10
            )
            
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Executa a query
                cursor.execute(query)
                
                # Verifica se é SELECT
                if query.strip().upper().startswith('SELECT') or \
                   query.strip().upper().startswith('SHOW'):
                    results = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    
                    # Converte RealDictRow para dict normal
                    rows = [dict(row) for row in results]
                    
                    return {
                        'success': True,
                        'type': 'select',
                        'columns': columns,
                        'rows': rows,
                        'row_count': len(rows)
                    }
                else:
                    # INSERT, UPDATE, DELETE, etc
                    connection.commit()
                    return {
                        'success': True,
                        'type': 'modify',
                        'affected_rows': cursor.rowcount,
                        'message': f'{cursor.rowcount} linha(s) afetada(s)'
                    }
            
        except psycopg2.Error as e:
            return {
                'success': False,
                'message': f'Erro PostgreSQL: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao executar query: {str(e)}'
            }
        finally:
            if connection:
                connection.close()
    
    def test_connection(self, engine, host, port, database, username, password):
        """
        Testa a conexão com o banco de dados
        
        Args:
            engine (str): Tipo do banco (mysql, postgres)
            host (str): Host
            port (int): Porta
            database (str): Nome do banco
            username (str): Usuário
            password (str): Senha
        
        Returns:
            dict: Resultado do teste
        """
        try:
            if engine in ['mysql', 'mariadb']:
                connection = pymysql.connect(
                    host=host,
                    port=port,
                    user=username,
                    password=password,
                    database=database,
                    connect_timeout=5
                )
                connection.close()
                
            elif engine == 'postgres':
                connection = psycopg2.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=username,
                    password=password,
                    connect_timeout=5
                )
                connection.close()
            
            else:
                return {
                    'success': False,
                    'message': f'Engine não suportado: {engine}'
                }
            
            return {
                'success': True,
                'message': 'Conexão estabelecida com sucesso!'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Falha na conexão: {str(e)}'
            }
    
    def get_tables(self, engine, host, port, database, username, password):
        """
        Lista as tabelas do banco de dados
        
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
        try:
            if engine in ['mysql', 'mariadb']:
                query = "SHOW TABLES"
                result = self.execute_query_mysql(host, port, database, username, password, query)
                
                if result['success']:
                    # Extrai nomes das tabelas
                    tables = [list(row.values())[0] for row in result['rows']]
                    return {
                        'success': True,
                        'tables': tables,
                        'count': len(tables)
                    }
                return result
                
            elif engine == 'postgres':
                query = "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
                result = self.execute_query_postgresql(host, port, database, username, password, query)
                
                if result['success']:
                    tables = [row['tablename'] for row in result['rows']]
                    return {
                        'success': True,
                        'tables': tables,
                        'count': len(tables)
                    }
                return result
            
            else:
                return {
                    'success': False,
                    'message': f'Engine não suportado: {engine}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao listar tabelas: {str(e)}'
            }
