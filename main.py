import os
import psycopg2
import datetime
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify

app = Flask(__name__)

# Pull local or production Postgres database credentials
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost/xvenu_db')

# SMTP Email Configuration Settings
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD')

def send_expiry_email(client_email, days_left):
    """Sends a standardized email warning the client about subscription ending."""
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("[-] Email credentials missing. Skipping notification transmission.")
        return

    subject = f"Action Required: Your Xvenu Trading Bot Access Expires in {days_left} Days"
    body = f"""Hello,

This is an automated notification from Xvenu Automation Labs.

Your active rental window for the Bybit Trade Fi Core bot engine is scheduled to expire on your next billing gate.
To avoid any execution gaps or missing active market position cycles, please ensure your renewal payment processes cleanly.

If no payment signature is logged, your API routing profiles will drop from the 2% risk execution loop in exactly {days_left} days.

Renew your seat here: https://xvenu-labs.vercel.app

Best regards,
Xvenu Infrastructure Engine
"""

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = client_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, client_email, msg.as_string())
        print(f"[+] Warning email transmitted successfully to: {client_email}")
    except Exception as e:
        print(f"[-] Failed to distribute notification email to {client_email}: {e}")


@app.route('/webhook/gumroad', methods=['POST'])
def gumroad_webhook():
    """Listens to Gumroad checkout events to automatically set access dates."""
    data = request.form
    email = data.get('email')
    event = data.get('event') # e.g., 'sale' or 'subscription_cancelled'

    if not email:
        return jsonify({"error": "Missing client mapping context"}), 400

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        if event in ['sale', 'subscription_restart']:
            # Set next billing date exactly 30 days out from today
            renew_date = datetime.date.today() + datetime.timedelta(days=30)
            cursor.execute('''
                UPDATE subscribers SET status = 'ACTIVE', next_billing_date = %s
                WHERE email = %s;
            ''', (renew_date, email))
            print(f"[+] Gumroad Payment Logged: Activated {email} through {renew_date}")

        elif event in ['subscription_cancelled', 'subscription_duration_ended']:
            # Immediately flag as expired so trading loops safely step back
            cursor.execute('''
                UPDATE subscribers SET status = 'EXPIRED' WHERE email = %s;
            ''', (email,))
            print(f"[-] Gumroad Termination: Deactivated {email} API execution streams.")

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "verified"}), 200
        
    except Exception as e:
        print(f"[-] Webhook database error: {str(e)}")
        return jsonify({"error": "Internal synchronization failure"}), 500


@app.route('/cron/check-expiry', methods=['GET'])
def check_upcoming_expirations():
    """Daily cron route that finds clients expiring in exactly 5 days and emails them."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Calculate target date exactly 5 days from today
        target_warning_date = datetime.date.today() + datetime.timedelta(days=5)

        cursor.execute('''
            SELECT email FROM subscribers
            WHERE status = 'ACTIVE'
            AND next_billing_date = %s;
        ''', (target_warning_date,))

        expiring_clients = cursor.fetchall()

        for (email,) in expiring_clients:
            send_expiry_email(email, days_left=5)

        cursor.close()
        conn.close()
        return jsonify({"checked_date": str(target_warning_date), "notified_count": len(expiring_clients)}), 200
        
    except Exception as e:
        print(f"[-] Cron execution error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
