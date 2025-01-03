from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
import sqlite3
from functools import wraps
from datetime import timedelta
import os
from utils.password_utils import is_common_password

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()
bcrypt = Bcrypt(app)
app.permanent_session_lifetime = timedelta(minutes=5)

# Database initialization
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            #flash("Log in first, Please.")
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('tools'))  
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()

        #if user and bcrypt.check_password_hash(user[2], password):  # Password is in the 3rd column
        if user:
            hashed_password = user[3]
            if bcrypt.check_password_hash(hashed_password, password):
                session.permanent = True
                session['user'] = email
                session['logged_in'] = True
                flash('Login successful!', 'success')
                return redirect(url_for('tools'))
        else:
            flash('Invalid email or password', 'error')
        
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = c.fetchone()
        conn.close()
        
        if existing_user:
            flash("Your email address is already registered. Please use another one or log in.", "error")
            return redirect('/register')
        
        if is_common_password(password):
            flash("The password is too easy to guess. Please choose another one.", "error")
            return redirect('/register')
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                      (username, email, hashed_password))
            conn.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists.', 'danger')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/tools')
@login_required
def tools():
    #if 'user' not in session:
        #return redirect(url_for('login'))
    return render_template('tools.html')
    
@app.route('/tools/text')
@login_required
def text_tool():
    #if 'user' not in session:
    #    return redirect(url_for('login'))
    return render_template('text-tool.html')
    
@app.route('/logout')
def logout():
    #session.pop('user_id', None)
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
