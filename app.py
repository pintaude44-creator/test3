import os
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={
    r"/send": {
        "origins": [
            "https://nsfuels.xyz",
            "https://www.nsfuels.xyz",
            "http://127.0.0.1:5500",
            "http://localhost:5500"
        ],
        "supports_credentials": False,
        "allow_headers": ["Content-Type"],
        "methods": ["POST", "OPTIONS"]
    }
})

EMAIL_USER = os.getenv("EMAIL_USER")          # seu Gmail (remetente)
EMAIL_PASS = os.getenv("EMAIL_PASS")          # App Password do Gmail
EMAIL_TO   = os.getenv("EMAIL_TO") or "pintaude44@gmail.com"  # destinatário

@app.route("/", methods=["GET"])
def health():
    return "OK", 200

@app.route("/send", methods=["POST","OPTIONS"])
def send():
    if request.method == "OPTIONS":
        # preflight do CORS
        return ("", 204)

    data = request.get_json(silent=True) or {}
    nome = data.get("nome", "").strip()
    email = data.get("email", "").strip()
    empresa = data.get("empresa", "").strip()
    mensagem = data.get("mensagem", "").strip()

    if not (nome and email and mensagem):
        return jsonify({"ok": False, "error": "Campos obrigatórios ausentes."}), 400

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[NSFuels] Contato de {nome}"
        msg["From"] = EMAIL_USER
        msg["To"] = EMAIL_TO

        html = f"""
        <h2>Novo contato pelo site</h2>
        <p><b>Nome:</b> {nome}</p>
        <p><b>E-mail:</b> {email}</p>
        <p><b>Empresa:</b> {empresa}</p>
        <p><b>Mensagem:</b><br>{mensagem.replace('\n','<br>')}</p>
        """
        msg.attach(MIMEText(html, "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())

        return jsonify({"ok": True}), 200

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
