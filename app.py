from flask import Flask, render_template, jsonify, request
import requests
import random
import string
import re

app = Flask(__name__)

DOMAINS = [
    "1secmail.com",
    "1secmail.org",
    "1secmail.net"
]

# generate random email
def random_email():
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    domain = random.choice(DOMAINS)
    return f"{name}@{domain}"

# extract otp code
def extract_otp(text):
    match = re.search(r"\b(\d{4,8})\b", text)
    if match:
        return match.group(1)
    return None

@app.route("/")
def home():
    return render_template("index.html")


# ===== GENERATE EMAIL =====
@app.route("/generate")
def generate():
    email = random_email()
    return jsonify({"email": email})


# ===== GET OTP =====
@app.route("/get_otp")
def get_otp():
    email = request.args.get("email")

    if not email:
        return jsonify({"otp": None})

    login, domain = email.split("@")

    # cek inbox
    url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
    messages = requests.get(url).json()

    if len(messages) == 0:
        return jsonify({"otp": None})

    # ambil email terbaru
    mail_id = messages[0]["id"]

    # baca isi email
    read_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={mail_id}"
    mail = requests.get(read_url).json()

    body = (mail.get("body") or "") + (mail.get("textBody") or "")

    otp = extract_otp(body)

    return jsonify({"otp": otp})


if __name__ == "__main__":
    app.run()
