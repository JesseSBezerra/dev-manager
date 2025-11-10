from flask import Blueprint, render_template, request, jsonify
from src.business.db_query_business import DatabaseQueryBusiness
from src.business.ec2_business import EC2Business
from src.business.rds_business import RDSBusiness
from src.database.db_manager import DatabaseManager

# Cria o Blueprint para o controller de Database Query
db_query_bp = Blueprint('db_query', __name__, url_prefix='/db-query')

# Instancia as camadas de negócio
business = DatabaseQueryBusiness()
ec2_business = EC2Business()
rds_business = RDSBusiness()
db_manager = DatabaseManager()


@db_query_bp.route('/')
def index():
    """
    Renderiza a página principal do Query Tool
    """
    return render_template('db_query/index.html')


@db_query_bp.route('/test-connection', methods=['POST'])
def test_connection():
    """
    Testa conexão com o banco de dados
    
    Body JSON:
        engine: Tipo do banco (mysql, postgres, mariadb)
        host: Host (geralmente localhost)
        port: Porta
        database: Nome do banco
        username: Usuário
        password: Senha
    """
    try:
        data = request.get_json()
        
        result = business.test_connection(
            engine=data.get('engine'),
            host=data.get('host'),
            port=int(data.get('port', 0)),
            database=data.get('database'),
            username=data.get('username'),
            password=data.get('password')
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao testar conexão: {str(e)}'
        }), 500


@db_query_bp.route('/execute-query', methods=['POST'])
def execute_query():
    """
    Executa uma query SQL
    
    Body JSON:
        engine: Tipo do banco
        host: Host
        port: Porta
        database: Nome do banco
        username: Usuário
        password: Senha
        query: Query SQL
    """
    try:
        data = request.get_json()
        
        result = business.execute_query(
            engine=data.get('engine'),
            host=data.get('host'),
            port=int(data.get('port', 0)),
            database=data.get('database'),
            username=data.get('username'),
            password=data.get('password'),
            query=data.get('query')
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao executar query: {str(e)}'
        }), 500


@db_query_bp.route('/get-tables', methods=['POST'])
def get_tables():
    """
    Lista as tabelas do banco de dados
    
    Body JSON:
        engine: Tipo do banco
        host: Host
        port: Porta
        database: Nome do banco
        username: Usuário
        password: Senha
    """
    try:
        data = request.get_json()
        
        result = business.get_tables(
            engine=data.get('engine'),
            host=data.get('host'),
            port=int(data.get('port', 0)),
            database=data.get('database'),
            username=data.get('username'),
            password=data.get('password')
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar tabelas: {str(e)}'
        }), 500


@db_query_bp.route('/create-tunnel', methods=['POST'])
def create_tunnel():
    """
    Cria um túnel SSM para o RDS
    
    Body JSON:
        bastion_instance_id: ID do Bastion
        rds_endpoint: Endpoint do RDS
        rds_port: Porta do RDS
        local_port: Porta local (opcional)
    """
    try:
        data = request.get_json()
        
        result = business.create_tunnel(
            bastion_instance_id=data.get('bastion_instance_id'),
            rds_endpoint=data.get('rds_endpoint'),
            rds_port=int(data.get('rds_port', 0)),
            local_port=int(data.get('local_port')) if data.get('local_port') else None
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao criar túnel: {str(e)}'
        }), 500


@db_query_bp.route('/close-tunnel', methods=['POST'])
def close_tunnel():
    """
    Fecha um túnel SSM ativo
    
    Body JSON:
        tunnel_key: Chave do túnel
    """
    try:
        data = request.get_json()
        
        result = business.close_tunnel(
            tunnel_key=data.get('tunnel_key')
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao fechar túnel: {str(e)}'
        }), 500


@db_query_bp.route('/list-bastions', methods=['GET'])
def list_bastions():
    """
    Lista instâncias EC2 do tipo Bastion
    """
    try:
        result = ec2_business.list_all_instances()
        
        if result['success']:
            # Filtra apenas Bastions que estão rodando
            bastions = [
                {
                    'instance_id': inst['instance_id'],
                    'name': inst['name'],
                    'state': inst['state'],
                    'private_ip': inst['private_ip']
                }
                for inst in result['instances']
                if inst['type_tag'] == 'Bastion' and inst['state'] == 'running'
            ]
            
            return jsonify({
                'success': True,
                'bastions': bastions,
                'count': len(bastions)
            }), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar Bastions: {str(e)}'
        }), 500


@db_query_bp.route('/list-rds', methods=['GET'])
def list_rds():
    """
    Lista instâncias RDS disponíveis
    """
    try:
        result = rds_business.list_all_instances()
        
        if result['success']:
            # Formata para o dropdown
            rds_list = [
                {
                    'identifier': inst['identifier'],
                    'endpoint': inst['endpoint'],
                    'port': inst['port'],
                    'engine': inst['engine'],
                    'status': inst['status']
                }
                for inst in result['instances']
                if inst['status'] == 'available' and inst['endpoint'] != 'N/A'
            ]
            
            return jsonify({
                'success': True,
                'rds_instances': rds_list,
                'count': len(rds_list)
            }), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar RDS: {str(e)}'
        }), 500


# ==================== TÚNEIS SALVOS ====================

@db_query_bp.route('/tunnels', methods=['GET'])
def get_tunnels():
    """
    Lista todos os túneis salvos
    """
    try:
        result = db_manager.get_saved_tunnels()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar túneis: {str(e)}'
        }), 500


@db_query_bp.route('/tunnels/<int:tunnel_id>', methods=['GET'])
def get_tunnel(tunnel_id):
    """
    Obtém um túnel específico
    """
    try:
        result = db_manager.get_tunnel(tunnel_id)
        return jsonify(result), 200 if result['success'] else 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter túnel: {str(e)}'
        }), 500


@db_query_bp.route('/tunnels', methods=['POST'])
def save_tunnel():
    """
    Salva um túnel SSH
    
    Body JSON:
        name: Nome do túnel
        bastion_id: ID da instância bastion
        db_host: Host do banco
        db_port: Porta do banco
        db_name: Nome do banco
        db_user: Usuário do banco
        db_password: Senha do banco (opcional)
        db_type: Tipo do banco (mysql, postgres)
        description: Descrição (opcional)
    """
    try:
        data = request.get_json()
        
        result = db_manager.save_tunnel(
            name=data.get('name'),
            bastion_id=data.get('bastion_id'),
            db_host=data.get('db_host'),
            db_port=data.get('db_port'),
            db_name=data.get('db_name'),
            db_user=data.get('db_user'),
            db_type=data.get('db_type'),
            db_password=data.get('db_password'),
            description=data.get('description')
        )
        
        return jsonify(result), 201 if result['success'] else 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao salvar túnel: {str(e)}'
        }), 500


@db_query_bp.route('/tunnels/<int:tunnel_id>', methods=['DELETE'])
def delete_tunnel(tunnel_id):
    """
    Deleta um túnel salvo
    """
    try:
        result = db_manager.delete_tunnel(tunnel_id)
        return jsonify(result), 200 if result['success'] else 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao deletar túnel: {str(e)}'
        }), 500


# ==================== COMANDOS SQL SALVOS ====================

@db_query_bp.route('/sql-commands', methods=['GET'])
def get_sql_commands():
    """
    Lista comandos SQL salvos
    
    Query params:
        tunnel_id: ID do túnel para filtrar (opcional)
    """
    try:
        tunnel_id = request.args.get('tunnel_id', type=int)
        result = db_manager.get_sql_commands(tunnel_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar comandos: {str(e)}'
        }), 500


@db_query_bp.route('/sql-commands', methods=['POST'])
def save_sql_command():
    """
    Salva um comando SQL
    
    Body JSON:
        tunnel_id: ID do túnel (opcional)
        name: Nome do comando
        sql_command: Comando SQL
        description: Descrição (opcional)
    """
    try:
        data = request.get_json()
        
        result = db_manager.save_sql_command(
            tunnel_id=data.get('tunnel_id'),
            name=data.get('name'),
            sql_command=data.get('sql_command'),
            description=data.get('description')
        )
        
        return jsonify(result), 201 if result['success'] else 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao salvar comando: {str(e)}'
        }), 500


@db_query_bp.route('/sql-commands/<int:command_id>', methods=['DELETE'])
def delete_sql_command(command_id):
    """
    Deleta um comando SQL salvo
    """
    try:
        result = db_manager.delete_sql_command(command_id)
        return jsonify(result), 200 if result['success'] else 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao deletar comando: {str(e)}'
        }), 500
