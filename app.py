from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from sqlalchemy import true
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Localization
messages = []
users = []


# SQLAlchemy configuration for MySQL (XAMPP)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/starbox'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# DATABASE DEFINITION
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Message(db.Model):
    __tablename__ = 'send_message'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    target = db.Column(db.String(255), nullable=False)
    message = db.Column(db.String(255), nullable=False)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    else:
        return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = next((user for user in users if user["username"] == username), None)

    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
        session['username'] = username
        return jsonify({'status': 'success', 'message': 'Login successful! Please wait.', 'redirect_url': url_for('home')})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    user_exists = any(user["username"] == username for user in users)

    # if User.query.filter_by(username=username).first():
    #     return jsonify({'status': 'error', 'message': 'Username already exists'}), 409
    if password != confirm_password:
        return jsonify({'status': 'error', 'message': 'Passwords do not match'}), 400
    
    if user_exists:
        return jsonify({'status': 'error', 'message': 'Username already exists'}), 409

    salt = bcrypt.gensalt(rounds=5)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    users.append({
        'username' : username,
        'password' : hashed_password
    })

    print(users)

    return jsonify({'status': 'success', 'message': 'User registered successfully!'})

@app.route('/submitMessage', methods=['POST'])
def submitMessage():
    target = request.form.get('target')
    message = request.form.get('message')

    if message and 0 < len(message) <= 70:
        messages.append({
            'target': target,
            'message': message
        })
        print(messages)
        return jsonify({'status': 'success', 'message': 'Message sent to user!'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid message length!'})

@app.route('/home')
def home():
    if 'username' in session:
        messages_data = [message for message in messages if message['target'] == session['username']]
    else:
        return redirect(url_for('index'))

    return render_template('home.html', messages=messages_data, session=session['username'])

@app.route('/send/<target>')
def send(target):
    return render_template('sendMessage.html', target=target)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=true)