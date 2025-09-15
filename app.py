import os
import smtplib
import socket
from flask import Flask, request, jsonify
from flask_cors import CORS
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ------------ Config ------------
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.hostinger.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("comercial@nsfuels.xyz")               # ex: contato@nsfuels.xyz
SMTP_PASS = os.getenv("3f:Ef$LYkBu")               # senha do email Hostinger
TO_EMAIL  = os.getenv("comercial@nsfuels.xyz", SMTP_USER)     # pra onde enviar (pode ser o mesmo)
ALLOW_ORIGIN = os.getenv("https://nsfuels.xyz/", "*")    # ex: https://nsfuels.xyz

# ------------ App ------------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ALLOW_ORIGIN}})

@app.get("/")
def health():
    return "OK", 200

@app.post("/send")
def send():
    # JSON obrigatório
    if not request.is_json:
        return jsonify(ok=False, error="JSON obrigatório"), 400

    data = request.get_json(silent=True) or {}
    nome     = (data.get("nome") or "").strip()
    empresa  = (data.get("empresa") or "").strip()
    email    = (data.get("email") or "").strip()
    mensagem = (data.get("mensagem") or "").strip()

    # validação mínima
    if not nome or not email or not mensagem:
        return jsonify(ok=False, error="Preencha nome, e-mail e mensagem."), 400

    try:
        # Monta e-mail (texto + Reply-To do visitante)
        subject = f"[Site] Contato - {nome}" + (f" ({empresa})" if empresa else "")
        body = f"""\
Nome: {nome}
E-mail: {email}
Empresa: {empresa}

Mensagem:
{mensagem}
"""

        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"]   = TO_EMAIL
        msg["Subject"] = subject
        msg["Reply-To"] = email
        msg.attach(MIMEText(body, "plain", "utf-8"))

        # Envia via SMTP SSL
        socket.setdefaulttimeout(15)
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [TO_EMAIL], msg.as_string())

        return jsonify(ok=True, message="Enviado com sucesso.")

    except Exception as e:
        # Não vaze segredos; retorno enxuto
        return jsonify(ok=False, error="Falha ao enviar."), 500


if __name__ == "__main__":
    # modo local
    app.run(host="0.0.0.0", port=5000, debug=True)
