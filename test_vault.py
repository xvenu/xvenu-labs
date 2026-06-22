import sqlite3
from cryptography.fernet import Fernet
import os

# 1. Setup mock data
mock_email = "master_trader@xvenu.com"
mock_bybit_key = "mock_api_key_12345"
mock_bybit_secret = "mock_api_secret_67890"
mock_license = "XVENU-TEST-KEY"

print("🛠️ [PRE-CHECK] Initializing database schema...")

# 2. Open database connection and FORCE creation of the subscribers table
try:
    conn = sqlite3.connect("xvenu_vault.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            email TEXT UNIQUE,
            gumroad_license TEXT,
            bybit_api_key TEXT,
            bybit_api_secret TEXT,
            status TEXT
        );
    """)
    conn.commit()
    print("✅ Schema Ready: 'subscribers' table is active.")
except Exception as schema_err:
    print(f"❌ Schema Initialization Failed: {str(schema_err)}")
    exit(1)

print(f"✨ [TEST] Registering dummy tenant: {mock_email}...")

# 3. Get the encryption key (fallback to a random one if not set locally)
FERNET_KEY = os.environ.get("ENCRYPTION_KEY", Fernet.generate_key().decode())
cipher = Fernet(FERNET_KEY.encode())

# 4. Encrypt the credentials
encrypted_key = cipher.encrypt(mock_bybit_key.encode()).decode()
encrypted_secret = cipher.encrypt(mock_bybit_secret.encode()).decode()

# 5. Insert directly into the vault database
try:
    cursor.execute("""
        INSERT INTO subscribers (email, gumroad_license, bybit_api_key, bybit_api_secret, status)
        VALUES (?, ?, ?, ?, 'ACTIVE')
        ON CONFLICT(email) DO UPDATE SET
            gumroad_license=excluded.gumroad_license,
            bybit_api_key=excluded.bybit_api_key,
            bybit_api_secret=excluded.bybit_api_secret,
            status='ACTIVE';
    """, (mock_email, mock_license, encrypted_key, encrypted_secret))
    
    conn.commit()
    print("✅ Success: Test user record inserted into xvenu_vault.db!")
    
    # 6. Read it back out to verify decryption works
    cursor.execute("SELECT bybit_api_key, bybit_api_secret FROM subscribers WHERE email=?", (mock_email,))
    row = cursor.fetchone()
    
    decrypted_k = cipher.decrypt(row[0].encode()).decode()
    decrypted_s = cipher.decrypt(row[1].encode()).decode()
    
    print(f"🔑 [VERIFICATION] Decrypted Key: {decrypted_k}")
    print(f"🔐 [VERIFICATION] Decrypted Secret: {decrypted_s}")
    print("🎯 Database encryption and storage loop verified 100% working!")
    
    conn.close()

except Exception as e:
    print(f"❌ Test Failed: {str(e)}")
