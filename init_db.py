import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')

def init_database():
    if not DATABASE_URL:
        print("[-] Missing DATABASE_URL environment variable.")
        return
        
    print("[+] Connecting to Render production database...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            bybit_api_key TEXT NOT NULL,
            bybit_api_secret TEXT NOT NULL,
            subscription_status VARCHAR(50) DEFAULT 'active',
            next_billing_date DATE
        );
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
    print("[+] Database initialized with rental tracking schema on Render.")

if __name__ == "__main__":
    init_database()
