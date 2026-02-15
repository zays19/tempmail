from flask import Flask, jsonify, render_template
import requests
import re
import os

app = Flask(__name__)

# halaman utama
@app.route("/")
def home():
    return render_template("index.html")

# generate email
@app.route("/api/new")
def new_mail():
    r = requests.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1")
    return jsonify({"email": r.json()[0]})


# ekstrak OTP
def extract_otp(text):
    codes = re.findall(r"\b\d{4,8}\b", text)
    if codes:
        return codes[0]
    return None


# cek OTP langsung
@app.route("/api/otp/<login>/<domain>")
def get_otp(login, domain):
    try:
        msgs = requests.get(
            f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}",
            timeout=10
        ).json()

        if not msgs:
            return jsonify({"otp": None})

        msg_id = msgs[0]["id"]

        mail = requests.get(
            f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={msg_id}",
            timeout=10
        ).json()

        body = (mail.get("body") or "") + (mail.get("textBody") or "")
        otp = extract_otp(body)

        return jsonify({"otp": otp})
    except:
        return jsonify({"otp": None})



