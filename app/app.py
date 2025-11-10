from flask import Flask, redirect, url_for
from src.controller.dynamodb_controller import dynamodb_bp
from src.controller.ecs_controller import ecs_bp
from src.controller.rds_controller import rds_bp
from src.controller.ec2_controller import ec2_bp
from src.controller.db_query_controller import db_query_bp
from src.controller.secrets_controller import secrets_bp
from src.controller.cloudwatch_controller import cloudwatch_bp
from src.controller.parameter_store_controller import parameters_bp
from src.controller.api_catalog_controller import api_catalog_bp
from src.controller.messaging_controller import messaging_bp
from src.controller.kafka_controller import kafka_bp
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Cria a aplicação Flask
app = Flask(__name__)

# Configurações da aplicação
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True') == 'True'

# Registra os Blueprints (Controllers)
app.register_blueprint(dynamodb_bp)
app.register_blueprint(ecs_bp)
app.register_blueprint(rds_bp)
app.register_blueprint(ec2_bp)
app.register_blueprint(db_query_bp)
app.register_blueprint(secrets_bp)
app.register_blueprint(cloudwatch_bp)
app.register_blueprint(parameters_bp)
app.register_blueprint(api_catalog_bp)
app.register_blueprint(messaging_bp)
app.register_blueprint(kafka_bp)


@app.route('/')
def index():
    """
    Rota principal - exibe página inicial com opções de serviços AWS
    """
    from flask import render_template
    return render_template('home.html')


@app.errorhandler(404)
def not_found(error):
    """
    Handler para erro 404
    """
    return {
        'success': False,
        'message': 'Recurso não encontrado',
        'error': '404 Not Found'
    }, 404


@app.errorhandler(500)
def internal_error(error):
    """
    Handler para erro 500
    """
    return {
        'success': False,
        'message': 'Erro interno do servidor',
        'error': '500 Internal Server Error'
    }, 500


if __name__ == '__main__':
    # Configurações do servidor
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    print(f"""
    ╔═══════════════════════════════════════════════════════╗
    ║            DEV Manager - Flask Application            ║
    ╚═══════════════════════════════════════════════════════╝
    
    🚀 Servidor iniciado com sucesso!
    
    📍 URL: http://{host}:{port}
    🔧 Modo: {'Desenvolvimento' if app.config['DEBUG'] else 'Produção'}
    
    ☁️  AWS Services:
       • DynamoDB - Gerenciamento de tabelas NoSQL
       • ECS - Visualização e controle de containers
       • RDS - Criação e gerenciamento de bancos de dados
       • EC2 - Instâncias e Bastion Hosts com SSM
       • Secrets Manager - Gerencie segredos e credenciais
       • CloudWatch Logs - Visualize logs e execute queries
       • Parameter Store - Gerencie parâmetros de configuração
       • SQS & SNS - Gerencie filas e tópicos de mensageria
    
    📡 APIs:
       • Catálogo - Gerencie e teste suas APIs
    
    🔄 Kafka:
       • Catálogo - Gerencie tópicos e publique mensagens
    
    🛠️  Dev Utils:
       • SQL Query Tool - Execute queries via Bastion/SSM
    
    ⚠️  Usando credenciais do AWS Toolkit
    
    """)
    
    app.run(host=host, port=port, debug=app.config['DEBUG'])
