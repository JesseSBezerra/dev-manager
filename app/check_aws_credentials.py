"""
Script para verificar onde o boto3 está encontrando credenciais
"""

import boto3
from botocore.credentials import get_credentials
from boto3 import Session
import os

print("=" * 60)
print("🔍 Verificando Credenciais AWS")
print("=" * 60)
print()

# Verifica variáveis de ambiente
print("📋 Variáveis de Ambiente:")
print(f"   AWS_PROFILE: {os.getenv('AWS_PROFILE', 'Não definida')}")
print(f"   AWS_REGION: {os.getenv('AWS_REGION', 'Não definida')}")
print(f"   AWS_ACCESS_KEY_ID: {'Definida' if os.getenv('AWS_ACCESS_KEY_ID') else 'Não definida'}")
print(f"   AWS_SECRET_ACCESS_KEY: {'Definida' if os.getenv('AWS_SECRET_ACCESS_KEY') else 'Não definida'}")
print(f"   AWS_SDK_LOAD_CONFIG: {os.getenv('AWS_SDK_LOAD_CONFIG', 'Não definida')}")
print()

# Verifica arquivo de credenciais
home = os.path.expanduser("~")
credentials_file = os.path.join(home, ".aws", "credentials")
config_file = os.path.join(home, ".aws", "config")

print("📁 Arquivos AWS:")
print(f"   Credentials: {credentials_file}")
print(f"   Existe? {'✅ Sim' if os.path.exists(credentials_file) else '❌ Não'}")
print(f"   Config: {config_file}")
print(f"   Existe? {'✅ Sim' if os.path.exists(config_file) else '❌ Não'}")
print()

# Tenta obter credenciais
print("🔑 Tentando obter credenciais...")
try:
    session = Session()
    credentials = session.get_credentials()
    
    if credentials:
        print("✅ Credenciais encontradas!")
        print(f"   Access Key: {credentials.access_key[:4]}...{credentials.access_key[-4:]}")
        print(f"   Método: {credentials.method if hasattr(credentials, 'method') else 'Desconhecido'}")
        
        # Tenta descobrir de onde vieram
        if hasattr(credentials, '_provider'):
            print(f"   Provider: {type(credentials._provider).__name__}")
    else:
        print("❌ Nenhuma credencial encontrada")
        
except Exception as e:
    print(f"❌ Erro ao obter credenciais: {e}")

print()
print("=" * 60)
print()

# Testa conexão
print("🧪 Testando conexão com DynamoDB...")
try:
    session = Session()
    client = session.client('dynamodb', region_name='sa-east-1')
    response = client.list_tables()
    print(f"✅ Conexão OK! {len(response['TableNames'])} tabelas encontradas")
except Exception as e:
    print(f"❌ Erro: {e}")

print()
input("Pressione ENTER para sair...")
