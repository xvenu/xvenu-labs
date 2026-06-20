import os
import psycopg2

# Securely grab your remote production connection string from Render
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_active_trading_credentials():
    """
    Queries the production database on Render. Returns ONLY clients
    who are marked as 'active' and whose 1-month rental window has not expired.
    """
    if not DATABASE_URL:
        print("[-] Error: DATABASE_URL environment variable is missing.")
        return []

    try:
        print("[+] Syncing with database to check active rental profiles...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # STRICT CUT-OFF: If next_billing_date is older than today, they are hidden automatically
        cursor.execute('''
            SELECT bybit_api_key, bybit_api_secret 
            FROM clients 
            WHERE subscription_status = 'active' 
            AND next_billing_date >= CURRENT_DATE;
        ''')
        
        active_vaults = cursor.fetchall()
        cursor.close()
        conn.close()
        
        print(f"[+] Successfully fetched {len(active_vaults)} active paying client portfolios.")
        return active_vaults

    except Exception as e:
        print(f"[-] Database connection error: {e}")
        return []

if __name__ == "__main__":
    # Test fetch block when running manually
    get_active_trading_credentials()
