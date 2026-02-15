from flask import Flask, render_template, jsonify, request
import requests
import re
import random
import string

app = Flask(__name__)

BASE = "https://temp-mail.app/api"

# generate random username (anti nabrak user)
def random_name():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))

# ambil email baru
@app.route("/generate")
def generate():
    try:
        name = random_name()
        res = requests.get(f"{BASE}/email/new?name={name}").json()
        return jsonify(res)
    except:
        return jsonify({"error":"failed"})

# cek inbox
@app.route("/check")
def check():
    email = request.args.get("email")

    try:
        res = requests.get(f"{BASE}/mail/list?email={email}").json()

        if not res:
            return jsonify({"otp": None})

        body = res[0].get("body","") + res[0].get("text","")

        # detect OTP (4-8 digit)
        match = re.search(r'\b\d{4,8}\b', body)
        if match:
            return jsonify({"otp": match.group()})

        return jsonify({"otp": None})

    except:
        return jsonify({"otp": None})

# bulk 5 email
@app.route("/bulk")
def bulk():
    emails = []
    for _ in range(5):
        name = random_name()
        res = requests.get(f"{BASE}/email/new?name={name}").json()
        emails.append(res.get("email"))
    return jsonify(emails)


@app.route("/")
def home():
    return render_template("index.html")
