from flask import Flask
from flask_mysqldb import MySQL
from app import app

app = Flask(__name__)

mysql = MySQL

mysql.init_app(app)