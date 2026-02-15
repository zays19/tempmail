from flask import Flask, render_template, jsonify, request
import requests
import re
import random
import string

app = Flask(__name__)

BASE = "https://temp-mail.app/api"

def random_name():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))


# generate email
@app.route("/generate")
def generate():
    try:
        name = random_name()
        res = requests.get(f"{BASE}/email/new?name={name}", timeout=15).json()

        mailbox = res.get("mailbox")
        domain = res.get("domain")
        token = res.get("token")

        email = f"{mailbox}@{domain}"

        return jsonify({
            "email": email,
            "token": token
        })
    except Exception as e:
        return jsonify({"error": str(e)})


# cek otp
@app.route("/check")
def check():
    token = request.args.get("token")

    try:
        res = requests.get(f"{BASE}/mail/list?token={token}", timeout=15).json()

        if not res:
            return jsonify({"otp": None})

        mail = res[0]
        body = (mail.get("body") or "") + (mail.get("text") or "")

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
        try:
            name = random_name()
            res = requests.get(f"{BASE}/email/new?name={name}", timeout=15).json()
            email = f"{res.get('mailbox')}@{res.get('domain')}"
            emails.append(email)
        except:
            pass

    return jsonify(emails)


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
