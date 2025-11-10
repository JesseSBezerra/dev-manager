"""
Script para criar IAM Role e Instance Profile para SSM manualmente
Execute este script se você tiver erros ao criar o Bastion Host
"""

import boto3
import time
from botocore.exceptions import ClientError

def create_ssm_role():
    """
    Cria IAM Role e Instance Profile para EC2 usar SSM Session Manager
    """
    print("=" * 60)
    print("🔧 Criando IAM Role para SSM Session Manager")
    print("=" * 60)
    print()
    
    try:
        iam_client = boto3.client('iam')
        
        role_name = 'EC2-SSM-Role'
        instance_profile_name = 'EC2-SSM-InstanceProfile'
        
        # 1. Verifica se já existe
        print("1️⃣  Verificando se já existe...")
        try:
            response = iam_client.get_instance_profile(InstanceProfileName=instance_profile_name)
            if response['InstanceProfile'].get('Roles'):
                print(f"✅ Instance Profile '{instance_profile_name}' já existe e está configurado!")
                print(f"   Role anexada: {response['InstanceProfile']['Roles'][0]['RoleName']}")
                return True
        except ClientError as e:
            if e.response['Error']['Code'] != 'NoSuchEntity':
                raise
            print(f"   Instance Profile não existe, será criado...")
        
        # 2. Cria a Role
        print(f"\n2️⃣  Criando Role '{role_name}'...")
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "ec2.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }
        
        try:
            iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=str(trust_policy).replace("'", '"'),
                Description='Role for EC2 instances to use SSM Session Manager',
                Tags=[
                    {'Key': 'ManagedBy', 'Value': 'AWSManager'},
                    {'Key': 'Purpose', 'Value': 'SSM-SessionManager'}
                ]
            )
            print(f"✅ Role '{role_name}' criada com sucesso!")
            time.sleep(2)
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                print(f"ℹ️  Role '{role_name}' já existe")
            else:
                raise
        
        # 3. Anexa a policy
        print(f"\n3️⃣  Anexando policy SSM à role...")
        try:
            iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore'
            )
            print(f"✅ Policy 'AmazonSSMManagedInstanceCore' anexada!")
        except ClientError as e:
            if 'already attached' in str(e):
                print(f"ℹ️  Policy já está anexada")
            else:
                raise
        
        # 4. Cria Instance Profile
        print(f"\n4️⃣  Criando Instance Profile '{instance_profile_name}'...")
        try:
            iam_client.create_instance_profile(
                InstanceProfileName=instance_profile_name,
                Tags=[
                    {'Key': 'ManagedBy', 'Value': 'AWSManager'},
                    {'Key': 'Purpose', 'Value': 'SSM-SessionManager'}
                ]
            )
            print(f"✅ Instance Profile '{instance_profile_name}' criado!")
            time.sleep(2)
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                print(f"ℹ️  Instance Profile '{instance_profile_name}' já existe")
            else:
                raise
        
        # 5. Adiciona Role ao Instance Profile
        print(f"\n5️⃣  Adicionando role ao instance profile...")
        try:
            iam_client.add_role_to_instance_profile(
                InstanceProfileName=instance_profile_name,
                RoleName=role_name
            )
            print(f"✅ Role adicionada ao Instance Profile!")
        except ClientError as e:
            if 'Cannot exceed quota' in str(e) or 'already contains' in str(e):
                print(f"ℹ️  Role já está no Instance Profile")
            else:
                raise
        
        # 6. Aguarda propagação
        print(f"\n6️⃣  Aguardando propagação do IAM...")
        for i in range(10, 0, -1):
            print(f"   {i} segundos...", end='\r')
            time.sleep(1)
        print("   ✅ Propagação concluída!      ")
        
        # 7. Verifica
        print(f"\n7️⃣  Verificando configuração...")
        response = iam_client.get_instance_profile(InstanceProfileName=instance_profile_name)
        profile = response['InstanceProfile']
        
        print(f"\n{'=' * 60}")
        print(f"✅ SUCESSO! IAM Role configurada corretamente")
        print(f"{'=' * 60}")
        print(f"\n📋 Detalhes:")
        print(f"   Instance Profile: {profile['InstanceProfileName']}")
        print(f"   ARN: {profile['Arn']}")
        if profile.get('Roles'):
            print(f"   Role anexada: {profile['Roles'][0]['RoleName']}")
        print(f"\n💡 Agora você pode criar Bastion Hosts com SSM!")
        print(f"   Acesse: http://localhost:5000/ec2")
        print()
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        
        print(f"\n❌ Erro: {error_code}")
        print(f"   {error_msg}")
        
        if error_code == 'AccessDenied':
            print(f"\n💡 Solução:")
            print(f"   Você não tem permissões IAM suficientes.")
            print(f"   Peça ao administrador AWS para:")
            print(f"   1. Criar a role 'EC2-SSM-Role'")
            print(f"   2. Anexar a policy 'AmazonSSMManagedInstanceCore'")
            print(f"   3. Criar o instance profile 'EC2-SSM-InstanceProfile'")
            print(f"   4. Adicionar a role ao instance profile")
        
        return False
        
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
        return False


if __name__ == '__main__':
    print()
    success = create_ssm_role()
    
    if not success:
        print(f"\n⚠️  Falha ao criar IAM Role")
        print(f"   Você ainda pode criar instâncias EC2, mas sem SSM")
        print(f"   Ou anexe o Instance Profile manualmente depois")
    
    print()
    input("Pressione ENTER para sair...")
