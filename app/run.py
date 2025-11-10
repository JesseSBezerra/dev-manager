"""
Script de inicialização da aplicação Flask
Execute este arquivo para iniciar o servidor
"""

from app import app
import os

if __name__ == '__main__':
    # Configurações do servidor
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    print(f"""
    ╔═══════════════════════════════════════════════════════╗
    ║         DynamoDB Manager - Flask Application          ║
    ╚═══════════════════════════════════════════════════════╝
    
    🚀 Servidor iniciado com sucesso!
    
    📍 URL Local: http://localhost:{port}
    📍 URL Rede: http://{host}:{port}
    🔧 Modo: {'Desenvolvimento' if debug else 'Produção'}
    
    ⚠️  IMPORTANTE:
    - Configure as credenciais AWS no arquivo .env
    - Ou use o AWS Toolkit para autenticação automática
    
    📚 Documentação: Veja o README.md para mais informações
    
    Pressione CTRL+C para parar o servidor
    """)
    
    app.run(host=host, port=port, debug=debug)
