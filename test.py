from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'user1'
app.config['MYSQL_PASSWORD'] = 'Qwer1234!'
app.config['MYSQL_DB'] = 'db'

mysql = MySQL(app)
#mysql.init_app(app)

@app.route('/')
def forside():
    return render_template ('forside.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "POST":
        username = request.form[username]
        password = request.form[password]
        
        cur = mysql.connection.cursor()
        
        cur.Execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cur.fetchone()
        cur.close()
        
        if user:
            session ['user_id'] = user['id']
            return redirect(url_for('profile'))
        else:
            error = 'fejl login'
            return render_template ('login.html', error=error)
    return render_template ('login.html')


@app.route('/')
def Create_Database():
    cur = mysql.connection.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INT AUTO_INCREMENT PRIMARY KEY, 
        username VARCHAR(255), 
        password VARCHAR(255),
        email VARCHAR(255)
    
        )''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS Virksomhed (
        virksomhed_id INT AUTO_INCREMENT PRIMARY KEY, 
        name VARCHAR(255), 
        email VARCHAR(255),
        beskrivelse TEXT,
        bruger_id INT NOT NULL,
        FOREIGN KEY (bruger_id) REFERENCES users(user_id))''')
    cur.execute(''' CREATE TABLE IF NOT EXISTS ledige (
        ledige_id INT AUTO_INCREMENT PRIMARY KEY, 
        name VARCHAR(255), 
        email VARCHAR(255),
        beskrivelse TEXT,
        cv TEXT,
        bruger_id INT NOT NULL,
        FOREIGN KEY (bruger_id) REFERENCES users(user_id))''')
    cur.execute(''' CREATE TABLE IF NOT EXISTS beskeder (
        beskeder_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        emne VARCHAR(255) NOT NULL,
        tekst TEXT NOT NULL,
        afsender_id INT NOT NULL,
        modtager_id INT NOT NULL,
        FOREIGN KEY (afsender_id) REFERENCES users(user_id),
        FOREIGN KEY (modtager_id) REFERENCES users(user_id))''')

    mysql.connection.commit()
    
    cur.close()
    return render_template('index.html')


@app.route('/opret_bruger', methods=['POST'])
def add ():
    
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (username, password, ema;il) VALUES (%s, %s, %s)", (username, password, email))
    mysql.connection.commit()
    cur.close()
    return render_template("opret_bruger.html", message='Data er gemt')

@app.route('/opret_bruger', methods= ['GET'])
def getall ():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.close()
    return render_template ('opret_bruger.html', users=users)

@app.route('/profile')

def profile():
    user_id = session.get('user_id')
    
    if not user_id:
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    
    cur.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
    user = cur.fetchone()
    
    cur.close()
    return render_template ('profile.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)