"""
Script para testar a conexão com AWS DynamoDB
Execute este script para verificar se suas credenciais estão funcionando
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def test_connection():
    print("=" * 60)
    print("🧪 Testando Conexão com AWS DynamoDB")
    print("=" * 60)
    print()
    
    # Verifica variáveis de ambiente
    print("📋 Verificando configurações:")
    print(f"   AWS_REGION: {os.getenv('AWS_REGION', 'Não definida (usando padrão)')}")
    
    aws_key = os.getenv('AWS_ACCESS_KEY_ID')
    if aws_key:
        print(f"   AWS_ACCESS_KEY_ID: {aws_key[:4]}...{aws_key[-4:]} (definida)")
    else:
        print("   AWS_ACCESS_KEY_ID: Não definida (usando cadeia de credenciais)")
    
    aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
    if aws_secret:
        print("   AWS_SECRET_ACCESS_KEY: ****** (definida)")
    else:
        print("   AWS_SECRET_ACCESS_KEY: Não definida (usando cadeia de credenciais)")
    
    print()
    print("-" * 60)
    print()
    
    # Tenta conectar
    print("🔌 Tentando conectar ao DynamoDB...")
    
    try:
        # Cria cliente DynamoDB
        region = os.getenv('AWS_REGION', 'sa-east-1')
        
        # Se há credenciais no .env, usa elas
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        if aws_access_key and aws_secret_key:
            print("   Usando credenciais do arquivo .env")
            client = boto3.client(
                'dynamodb',
                region_name=region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
        else:
            print("   Usando cadeia de credenciais padrão (AWS Toolkit/CLI)")
            client = boto3.client('dynamodb', region_name=region)
        
        print()
        
        # Tenta listar tabelas
        print("📊 Listando tabelas DynamoDB...")
        response = client.list_tables()
        
        tables = response.get('TableNames', [])
        
        print()
        print("=" * 60)
        print("✅ CONEXÃO ESTABELECIDA COM SUCESSO!")
        print("=" * 60)
        print()
        
        if tables:
            print(f"📋 {len(tables)} tabela(s) encontrada(s):")
            for i, table in enumerate(tables, 1):
                print(f"   {i}. {table}")
        else:
            print("📋 Nenhuma tabela encontrada (isso é normal se você ainda não criou nenhuma)")
        
        print()
        print("🎉 Sua aplicação Flask está pronta para usar!")
        print()
        
        return True
        
    except NoCredentialsError:
        print()
        print("=" * 60)
        print("❌ ERRO: Credenciais não encontradas")
        print("=" * 60)
        print()
        print("Soluções possíveis:")
        print("1. Configure o AWS Toolkit no VS Code")
        print("2. Configure o AWS CLI: aws configure")
        print("3. Preencha o arquivo .env com suas credenciais")
        print()
        print("Veja o arquivo TROUBLESHOOTING.md para mais detalhes")
        print()
        return False
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        print()
        print("=" * 60)
        print(f"❌ ERRO AWS: {error_code}")
        print("=" * 60)
        print()
        print(f"Mensagem: {error_message}")
        print()
        
        if error_code == 'UnrecognizedClientException':
            print("Causa provável: Token de segurança inválido")
            print()
            print("Soluções:")
            print("1. Se usar AWS Toolkit: Reconecte-se no VS Code")
            print("2. Se usar .env: Verifique se as credenciais estão corretas")
            print("3. Deixe AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY vazios no .env")
            print("   para usar AWS Toolkit automaticamente")
        
        elif error_code == 'AccessDeniedException':
            print("Causa: Sem permissão para acessar DynamoDB")
            print()
            print("Solução:")
            print("Verifique se sua conta AWS tem as permissões:")
            print("- dynamodb:ListTables")
            print("- dynamodb:CreateTable")
            print("- dynamodb:DescribeTable")
            print("- dynamodb:DeleteTable")
        
        else:
            print("Veja o arquivo TROUBLESHOOTING.md para mais detalhes")
        
        print()
        return False
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERRO INESPERADO")
        print("=" * 60)
        print()
        print(f"Erro: {str(e)}")
        print()
        print("Veja o arquivo TROUBLESHOOTING.md para mais detalhes")
        print()
        return False


if __name__ == '__main__':
    success = test_connection()
    
    if success:
        print("✅ Execute agora: python app.py")
    else:
        print("❌ Corrija os erros acima antes de executar a aplicação")
    
    print()
    input("Pressione ENTER para sair...")
