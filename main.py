from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os

app = Flask(__name__)
# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = '1234'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'user1'
app.config['MYSQL_PASSWORD'] = 'Qwer1234!'
app.config['MYSQL_DB'] = 'db'

# Intialize MySQL
mysql = MySQL(app)


IMG_FOLDER = os.path.join('static', 'img')
cv_mappe= os.path.join('static', 'cv_mappe')
app.config['UPLOAD_FOLDER'] = IMG_FOLDER
app.config['UPLOAD_FOLDER2'] = cv_mappe
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}  # Tilladte filtyper



            
            
    
    





@app.route('/', methods=['GET', 'POST'])
def forside():
    img = os.path.join(app.config['UPLOAD_FOLDER'], 'ledige.jpg')
    return render_template('forside.html', user_image = img)


# http://localhost:5000/pythonlogin/ - the following will be our login page, which will use both GET and POST requests
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
        # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

                # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        
                # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['user_id'] = account['user_id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
            
            
    return render_template('index.html', msg='')

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('user_id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/registrer', methods=['GET', 'POST'])
def registrer():
    # Output message if something goes wrong...
    msg = ''
    
    # Check if "username", "password", "email", and "type" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'type' in request.form:
        
        # File upload handling
        cv = request.files['cv']
        if cv and allowed_file(cv.filename):
            cv.save(os.path.join(app.config['UPLOAD_FOLDER2'], cv.filename))
            # Gem filstien i databasen eller udfør de ønskede handlinger
            msg = 'CV uploaded successfully!'
        else:
            msg = 'Invalid file format! Allowed formats are: pdf, doc, docx'
        
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        type = request.form['type']  # 'type' er et reserveret ord, brug 'account_type' i stedet
        name = request.form['name']
        beskrivelse = request.form['beskrivelse']
        
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username =%s', (username,))
        account = cursor.fetchone()
        
    
        
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesn't exist and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s, %s)', (username, password, email, type,))
            user_id = cursor.lastrowid
            cursor.execute('INSERT INTO ledige (name, email, beskrivelse, cv, user_id) VALUES (%s, %s, %s, %s, %s)', (name, email, beskrivelse, cv.filename, user_id,))
            mysql.connection.commit()
            msg = 'Tillykke du har oprettet en profil'
            return render_template ('registrer.html', msg=msg)
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    
    # Show registration form with message (if any)
    return render_template('registrer.html', msg=msg)


# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/home', methods=['GET', 'POST'])
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        
        img = os.path.join(app.config['UPLOAD_FOLDER'], '1691809.jpg')
        return render_template('home.html', username=session['username'], user_image=img)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['user_id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        
        return render_template('profile.html', account=account)

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        cursor = mysql.connection.cursor()
        search_query = '%' + request.form['search'] + '%'
        cursor.execute('SELECT * FROM users WHERE username LIKE %s', (search_query,))
        records = cursor.fetchall()
        cursor.close()
        return render_template("result.html", records=records)
    return render_template("search.html")



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)