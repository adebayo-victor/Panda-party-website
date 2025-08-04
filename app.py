import random
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

@app.route("/login", methods=['POST'])
def login():
    try:
        if request.method == "POST":
            data = request.get_json()
            email = data['email']
            password = data['password']
            #validation with the db is done here
            valid = db.execute("SELECT * FROM clients WHERE email=? AND password_hash=?",email, password)
            if valid:
                reply = {"response":"successful", "url":"tickets_moi/" + f"{reply[0]['id']}"}
                print(reply)
                return "tickets_moi/" + f"{reply[0]['id']}"
            else:
                return{'response':"Not an existing client"}
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
    user_tickets = db.execute("SELEct * FROM ticket_purchases JOIN client ON ticket_purchases.client_id=client.id JOIN ticket_info ON ticket_purchases.id=ticket_info.id WHERE id = ?", user_id)
    tickets = db.execute("SELECT * FROM ticket_info")
    return "tickets page"
@app.route("/register")
def register():
    return render_template("register.html")
if __name__=="__main__":
    app.run(debug=True, port=5000 )