import os
import ssl
import smtplib
from email.message import EmailMessage
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# CORS (permite seu site)
ALLOW_ORIGIN = os.getenv("ALLOW_ORIGIN", "*")
CORS(app, resources={r"/*": {"origins": ALLOW_ORIGIN}})

@app.get("/")
def health():
    return "OK", 200

def handle_send():
    data = request.get_json(silent=True) or {}

    nome     = (data.get("nome") or "").strip()
    email    = (data.get("email") or "").strip()
    empresa  = (data.get("empresa") or "").strip()
    mensagem = (data.get("mensagem") or "").strip()

    if not nome or not email:
        return jsonify(ok=False, error="nome e email são obrigatórios"), 400

    # SMTP (Hostinger)
    smtp_host = os.getenv("SMTP_HOST", "smtp.hostinger.com")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    smtp_user = os.getenv("SMTP_USER") or os.getenv("EMAIL_USER")
    smtp_pass = os.getenv("SMTP_PASS") or os.getenv("EMAIL_PASS")

    mail_from = os.getenv("MAIL_FROM") or os.getenv("SENDER") or smtp_user
    mail_to   = os.getenv("MAIL_TO")   or os.getenv("RECIPIENT") or smtp_user

    if not smtp_user or not smtp_pass:
        return jsonify(ok=False, error="Credenciais SMTP ausentes"), 500

    subject = f"[Site NSFuels] Contato — {nome}"
    body = f"""Nome: {nome}
E-mail: {email}
Empresa: {empresa}

Mensagem:
{mensagem}
"""

    msg = EmailMessage()
    msg["From"] = mail_from
    msg["To"] = mail_to
    msg["Subject"] = subject
    msg["Reply-To"] = email
    msg.set_content(body)

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=ctx) as s:
            s.login(smtp_user, smtp_pass)
            s.send_message(msg)
        return jsonify(ok=True), 200
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

@app.post("/send")
def send_mail():
    return handle_send()

# Alias: aceita POST na raiz (se precisar)
@app.route("/", methods=["POST", "OPTIONS"], endpoint="send_root")
def send_root():
    if request.method == "OPTIONS":
        return "", 200
    return handle_send()

if __name__ == "__main__":
    # Render injeta PORT; se local, usa 10000
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
