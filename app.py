from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3
from functools import wraps
from datetime import timedelta
import os
from utils.password_utils import is_common_password
import numpy as np
from groq import Groq
import re

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()
bcrypt = Bcrypt(app)
app.permanent_session_lifetime = timedelta(minutes=5)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    #default_limits=["5 per minute"]
)

# Load test data from a .txt file
with open("trainingData2.txt", "r",encoding="utf-8") as f:
    test_data_content = f.read()
    

#use Groq API
client = Groq(
    api_key="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",  # Replace with your actual API key
)


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
@limiter.limit("5 per minute", key_func=get_remote_address)
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
                flash("Invalid email or password", "error")
        else:
            flash("Invalid email or password", "error")
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute", key_func=get_remote_address)
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

    return render_template('tools.html')
    
@app.route('/tools/text', methods=['GET', 'POST'])
@login_required
def text_tool():
    if request.method == 'POST':
        text_input = request.form['text_input']  # Get text from the form
        # Process the text and redirect to the feedback page
        return redirect(url_for('feedback', text=text_input))
        
    return render_template('text-tool.html')
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

#@app.route('/analyze-text', methods=['POST'])
#@login_required
#def analyze_text():
#    if request.method == "POST":
#        text_input = request.form['text_input']
        
        #predicted_percentages = prediction_module.predict(text_input)
        
        #return redirect(url_for('feedback', actual_values=predicted_percentages))
        
@app.route('/feedback', methods=['GET'])
@login_required
def feedback():
    #if request.method == 'POST':
    #    data = request.get_json()
    #    user_text = data.get("text")
    #else:
    user_text = request.args.get("text")  # Use GET to get text

    if not user_text:
        return jsonify({"feedback": "Text is required for evaluation."}), 400

    try:
           # Groq API request
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an evaluator using the 6P method "
                        "(Certainty, Variation, Connectedness, Significance, Contributions, and Growth). "
                        "Use the provided training data to guide your evaluation. To be balanced the sum of Certainty Variation and Connectedness should be 80% with error of 2"
                        "And the sum of Significance Contributions and Growth should be 20% wiht error of 2. "
                        "Then the sum of Variation Significance and Growth 39% with error of 2. And the sum of Certainty Connectedness and Contributions 61% with error of 2"
                        "If all of these conditions are met, then the system is cosidered balanced, if not - not balanced"
                        "The feedback structure should be like that: first is the entity name, then explanation , and the its score at the end, for example: Signifance: 'Explanation' . Score: 25% , then there will be the sums of each combination where it will show if it's within the error margin or not, for example: Certainty + Variation + Coonectedness= 67% (the ideal result is 80%+-2, it is unbalanced)"
                        "And the final advice should tell if system is balanced or not balanced. And if it is not balanced give the quick explanation why it is not balanced and how to fix it."
                        "The sum shouldn't exceed 100%"
                    ),
                },
                {
                    "role": "system",
                    "content": f"Training data: {test_data_content}",
                },
                {
                    "role": "user",
                    "content": user_text,
                },
            ],
        )

        # Extract feedback from the API response
        feedback = response.choices[0].message.content
        scores = re.findall(r'Score:\s(\d+)', feedback)
        
        scores = list(map(int, scores))
        print(scores)
        print(f"Feedback: {feedback}")  # Debug line
        if len(scores) != 6:
            raise ValueError("No se extrajeron los 6 puntajes esperados.")
        #return jsonify({"feedback": feedback})
        return render_template('feedback.html', feedback=feedback, scores=scores)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"feedback": "Failed to evaluate text. Please try again."}), 500


@app.route('/tools/image')
@login_required
def image_tool():
    return render_template('image-tool.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
