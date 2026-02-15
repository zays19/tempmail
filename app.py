from flask import Flask, render_template, jsonify, request
import requests
import random
import string
import re
import time
import secrets

app = Flask(__name__)

# ================= DOMAIN LIST =================
def get_domains():
    try:
        res = requests.get(
            "https://www.1secmail.com/api/v1/?action=getDomainList",
            timeout=8
        )
        domains = res.json()
        if isinstance(domains, list) and len(domains) > 0:
            return domains
    except:
        pass

    # fallback kalau API delay
    return [
        "1secmail.com",
        "1secmail.org",
        "1secmail.net",
        "esiix.com",
        "wwjmp.com",
        "yoggm.com",
        "qvy.me",
        "xojxe.com"
    ]


# ================= UNIQUE EMAIL =================
def random_email():
    domains = get_domains()

    # anti nabrak:
    # random + waktu + entropy
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    ts = str(int(time.time()))[-5:]
    entropy = secrets.token_hex(2)

    name = f"{rand}{ts}{entropy}"
    domain = random.choice(domains)
    return f"{name}@{domain}"


# ================= OTP EXTRACT =================
def extract_otp(text):
    if not text:
        return None

    match = re.search(r"\b(\d{4,8})\b", text)
    if match:
        return match.group(1)
    return None


@app.route("/")
def home():
    return render_template("index.html")


# ================= GENERATE SINGLE =================
@app.route("/generate")
def generate():
    return jsonify({"email": random_email()})


# ================= GENERATE BULK =================
@app.route("/generate_bulk")
def generate_bulk():
    emails = [random_email() for _ in range(5)]
    return jsonify({"emails": emails})


# ================= GET OTP =================
@app.route("/get_otp")
def get_otp():
    email = request.args.get("email")
    if not email:
        return jsonify({"otp": None})

    try:
        login, domain = email.split("@")

        inbox = requests.get(
            f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}",
            timeout=8
        ).json()

        if not inbox:
            return jsonify({"otp": None})

        mail_id = inbox[0]["id"]

        mail = requests.get(
            f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={mail_id}",
            timeout=8
        ).json()

        body = (mail.get("body") or "") + (mail.get("textBody") or "")
        otp = extract_otp(body)

        return jsonify({"otp": otp})

    except:
        return jsonify({"otp": None})
