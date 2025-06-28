from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['MYSQL_HOST'] = os.getenv('DB_HOST')
app.config['MYSQL_USER'] = os.getenv('DB_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASS')
app.config['MYSQL_DB'] = os.getenv('DB_NAME')

mysql = MySQL(app)

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, label, pos_x, pos_y, color_bg, color_fg, action FROM buttons ORDER BY id")
    buttons = cur.fetchall()
    return render_template('index.html', buttons=buttons)

if __name__ == '__main__':
    app.run(debug=True)
