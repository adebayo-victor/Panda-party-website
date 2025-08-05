import random
import string
import csv
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, session, url_for, jsonify, send_file
import pandas as pd
from flask_cors import CORS
from cs50 import SQL
import secrets
import os
from werkzeug.utils import secure_filename
import string
import io
import xlsxwriter
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("app_secret_key")
db = SQL('sqlite:///party.db')
load_dotenv()



def generate_six_digit_code():
    """Generates a random 6-digit code using digits."""
    return ''.join(random.choices(string.digits, k=6))

# Example usage:
code = generate_six_digit_code()
print(f"Generated 6-digit code: {code}")
@app.route("/login", methods=['POST'])
@app.route("/")
def index():
    return render_template("index.html")
def login():
    try:
        if request.method == "POST":
            data = request.get_json()
            email = data['email']
            password = data['password']
            #validation with the db is done here
            valid = db.execute("SELECT * FROM clients WHERE email=? AND password_hash=?",email, password)
            if valid:
                reply = {"response":"successful", "url":"tickets_moi/" + f"{valid[0]['id']}"}
                print(reply)
                return reply
            else:
                return {'response':"Not an existing client"}
    except Exception as e:
        return{'response':f"{e}"}
@app.route("/signup",methods=["POST"])
def signup():
    try:
        if request.method == "POST":
            data = request.get_json()
            name = data['name']
            email = data['email']
            password = data['password']
            phone = data['phone']
            #registration with the db is done here 
            registered = db.execute("INSERT INTO clients(name,email,password_hash,phone_number) VALUES(?,?,?,?)",name,email,password,phone)
            if registered:
                reply = registered
                return jsonify(reply)
    except Exception as e:
        return{'response':f"{e}"}
@app.route("/tickets_moi/<int:user_id>")
def tickets_moi(user_id):
    user = db.execute("SELECT * FROM clients WHERE id = ?", user_id)
    user_tickets = db.execute("SELECT * FROM clients JOIN ticket_purchases ON clients.id = ticket_purchases.client_id JOIN ticket_info ON ticket_info.id = ticket_purchases.ticket_id WHERE clients.id = ?", 4)
    tickets = db.execute("SELECT * FROM ticket_info")
    return render_template("regular.html", user=user,user_tickets=user_tickets, tickets=tickets )
@app.route("/register")
def register():
    return render_template("register.html")
PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
PAYSTACK_INITIALIZE_URL = 'https://api.paystack.co/transaction/initialize'
# 🔥 Step 1: Post session and initialize Paystack payment
@app.route('/paystack_init', methods=['POST'])
def post_session():
    try:
        data = request.form
        print(data)
        ticket_id = data.get("ticket_id")
        user_id = data.get("user_id")
        name = data.get("user_name")
        email = data.get("user_email")
        price = data.get("ticket_price")
        phone_number = data.get("phone_number")

        metadata = {
            "name": name,
            "email": email,
            "phone_number": phone_number,
            "ticket_id":ticket_id,
            "user_id":user_id
        }

        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "email": email,
            "amount": float(price) * 100,
            "metadata": metadata,
            "callback_url": "https://panda-party-website.onrender.com/callback"  # 🔁 Paystack will redirect here
        }

        response = requests.post(PAYSTACK_INITIALIZE_URL, json=payload, headers=headers)
        print(response)
        res_data = response.json()
        if res_data.get("status"):
            print(res_data) # This print is already there, you can keep it or remove it
            return redirect(res_data['data']['authorization_url'])

        else:
            print({"error": res_data})
            return {"error": res_data}
    except Exception as e:
        return {"error": str(e)}


# 🔁 Step 2: Payment verification callback
@app.route('/callback')
def callback():
    reference = request.args.get('reference')

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }

    res = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
    response_data = res.json()

    if not response_data.get('status'):
        return {"error": "Payment verification failed"}

    payment_data = response_data['data']
    metadata = payment_data['metadata']

    try:
        current_datetime = datetime.now()
        year = current_datetime.year
        month = current_datetime.month
        day = current_datetime.day
        hour = current_datetime.hour
        minute = current_datetime.minute
        second = current_datetime.second
        current = f"{year}-{month}-{day}-{hour}:{minute}:{second}"
        if db.execute("INSERT INTO ticket_purchases(client_id,ticket_id,purchase_date, unique_code, status) VALUES(?,?,?,?,?)",metadata["user_id"], metadata["ticket_id"], current, generate_six_digit_code(), "valid"):
            return render_template('success.html')  # or return a JSON response
    except IndexError as e:
        return {"error": str(e)}
@app.route("/validation", methods=["POST"])
def validation():
    if request.method == "POST":
        data = request.get_json()
        code = data["code"]
        valid = db.execute("SELECT * FROM ticket_purchases WHERE unique_code = ?", code)
        if valid:
            if valid[0]['status'] != "used":
                db.execute("UPDATE ticket_purchases SET status=? WHERE id = ?","used", valid[0]['id'])
                return {'response':"valid"}
            else:
                return {'response':"used"}
        else:
            return {'response':"invalid"}
@app.route("/validity")
def validity():
    return render_template("validity.html")
if __name__=="__main__":
    app.run(debug=True, port=5000 )