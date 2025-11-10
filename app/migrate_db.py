"""
Script de migração do banco de dados
Adiciona colunas que faltam nas tabelas existentes
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'app.db')

def migrate():
    print("🔄 Iniciando migração do banco de dados...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verifica se a coluna db_password existe em saved_tunnels
        cursor.execute("PRAGMA table_info(saved_tunnels)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'db_password' not in columns:
            print("  ➕ Adicionando coluna db_password na tabela saved_tunnels...")
            cursor.execute('ALTER TABLE saved_tunnels ADD COLUMN db_password TEXT')
            print("  ✅ Coluna db_password adicionada!")
        else:
            print("  ℹ️  Coluna db_password já existe")
        
        # Verifica se as colunas de test parameters existem em api_requests
        cursor.execute("PRAGMA table_info(api_requests)")
        api_columns = [col[1] for col in cursor.fetchall()]
        
        if 'last_test_body' not in api_columns:
            print("  ➕ Adicionando colunas de test parameters na tabela api_requests...")
            cursor.execute('ALTER TABLE api_requests ADD COLUMN last_test_body TEXT')
            cursor.execute('ALTER TABLE api_requests ADD COLUMN last_test_query TEXT')
            cursor.execute('ALTER TABLE api_requests ADD COLUMN last_test_headers TEXT')
            print("  ✅ Colunas de test parameters adicionadas!")
        else:
            print("  ℹ️  Colunas de test parameters já existem")
        
        # Verifica se a tabela saved_sql_commands existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='saved_sql_commands'")
        if not cursor.fetchone():
            print("  ➕ Criando tabela saved_sql_commands...")
            cursor.execute('''
                CREATE TABLE saved_sql_commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tunnel_id INTEGER,
                    name TEXT NOT NULL,
                    sql_command TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tunnel_id) REFERENCES saved_tunnels(id) ON DELETE CASCADE
                )
            ''')
            print("  ✅ Tabela saved_sql_commands criada!")
        else:
            print("  ℹ️  Tabela saved_sql_commands já existe")
        
        conn.commit()
        print("✅ Migração concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro na migração: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
