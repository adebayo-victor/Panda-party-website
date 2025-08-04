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
db = SQL('sqlite://party.db')

@app.route("/login", methods=['POST'])
def login():
    try:
        if request.method == "POST:
            data = request.get_json()
            email = data['email']
            #validation with the db is done here

            if valid:
                return jsonify(reply)
            else:
                return{'response':"Not an existing client"}
    except Exception as e:
        return{'response':f"{e}"}
@app.route("/signup",methods=["POST"])
def signup():
    try:
        if request.method == "POST:
            data = request.get_json()
            name = data['name']
            email = data['email']
            password = data['password']
            phone = data['phone']
            #registration with the db is done here 

            if registered:
                return jsonify(reply)
    except Exception as e:
        return{'response':f"{e}"}