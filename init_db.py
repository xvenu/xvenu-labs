import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')

def init_database():
    if not DATABASE_URL:
        print("[-] Missing DATABASE_URL environment variable.")
        return

    print("[+] Connecting to PostgreSQL database engine...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Creates the table matching your backend multi-tenant structure precisely
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                gumroad_license TEXT NOT NULL,
                bybit_api_key TEXT NOT NULL,
                bybit_api_secret TEXT NOT NULL,
                status VARCHAR(50) DEFAULT 'ACTIVE',
                next_billing_date DATE
            );
        ''')

        conn.commit()
        cursor.close()
        conn.close()
        print("[+] PostgreSQL Database initialized with verified tracking schema.")
    except Exception as e:
        print(f"[-] Database initialization failed: {str(e)}")

if __name__ == "__main__":
    init_database()
