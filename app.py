from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
import os
from flask_cors import CORS

CORS(app, resources={
    r"/send": {
        "origins": [
            "https://nsfuels.xyz",
            "https://www.nsfuels.xyz",
            "http://127.0.0.1:5500",
            "http://localhost:5500"
        ]
    }
})

app = Flask(__name__)

@app.route("/send", methods=["POST"])
def send_email():
    data = request.json

    nome = data.get("nome")
    email = data.get("email")
    empresa = data.get("empresa")
    mensagem = data.get("mensagem")

    corpo_email = f"""
    Novo contato do site NSGreen Fuels:

    Nome: {nome}
    Email: {email}
    Empresa: {empresa}
    Mensagem: {mensagem}
    """

    try:
        msg = MIMEText(corpo_email)
        msg["Subject"] = "Novo contato do site"
        msg["From"] = os.getenv("EMAIL_USER")
        msg["To"] = os.getenv("EMAIL_TO")

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
            server.sendmail(msg["From"], [msg["To"]], msg.as_string())

        return jsonify({"status": "success", "message": "Email enviado com sucesso!"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/")
def home():
    return "API do formulário funcionando!"

