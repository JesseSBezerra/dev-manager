import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Classe de configuração base para a aplicação Flask
    """
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # AWS
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    # Server
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))


class DevelopmentConfig(Config):
    """
    Configuração para ambiente de desenvolvimento
    """
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """
    Configuração para ambiente de produção
    """
    DEBUG = False
    FLASK_ENV = 'production'


class TestingConfig(Config):
    """
    Configuração para ambiente de testes
    """
    TESTING = True
    DEBUG = True


# Dicionário de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """
    Retorna a configuração baseada no ambiente
    
    Args:
        env (str): Nome do ambiente (development, production, testing)
    
    Returns:
        Config: Classe de configuração apropriada
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    return config.get(env, config['default'])
