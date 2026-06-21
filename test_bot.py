import sys
import time
import requests

# --- AUTHENTICATION CONFIGURATION ---
LICENSE_KEY = "TEST-UNAUTHORIZED-KEY"
AUTH_SERVER_URL = "https://c4b7c4748de7bb30-102-215-34-22.serveousercontent.com/api/v1/verify-license"

def verify_bot_license():
    print(f"[SYSTEM] Verifying license framework against auth server...")
    payload = {"license_key": LICENSE_KEY}
    
    try:
        response = requests.post(AUTH_SERVER_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ [AUTH SUCCESS] Welcome back: {data.get('email')}")
            print(f"[AUTH SUCCESS] Status: {data.get('message')}\n")
            return True
        elif response.status_code == 403:
            print("❌ [AUTH ERROR] Access Denied: Invalid, expired, or cancelled license key.")
            return False
        else:
            print(f"⚠️ [AUTH ERROR] Server returned unexpected code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ [CRITICAL] Failed to connect to xvenu labs authentication server. Execution halted.")
        return False

if __name__ == "__main__":
    if not verify_bot_license():
        print("[CRITICAL] Licensing validation failed. Terminating system process.")
        sys.exit(1)
        
    # --- CORE TRADING BOT ENGINE STARTUP ---
    print("🚀 [ENGINE] Licensing confirmed. Initializing XvenuBot Core V1...")
    print("[ENGINE] Allocating 2.00% capital risk ceiling per sequence.")
    print("[ENGINE] Monitoring channels for target asset triplets...")
    
    while True:
        print("[RUNLOOP] Polling Bybit V5 API market feeds...")
        time.sleep(5)

