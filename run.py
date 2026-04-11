import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import get_db
from werkzeug.utils import secure_filename 

app = Flask(__name__)
app.secret_key = 'super_secret_key'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/")
def index():
    return redirect(url_for("Dashboard"))