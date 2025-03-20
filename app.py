import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt
import os

app = Flask(__name__)

app.secret_key = os.urandom(24)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'expenses.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_BINDS'] = {
    'secondary': 'sqlite:///user.db'
}

db1 = SQLAlchemy(app)

class Expense(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    amount = db1.Column(db1.Float, nullable=False)
    date = db1.Column(db1.DateTime, nullable=False, default=datetime.utcnow)
    category = db1.Column(db1.String(50), nullable=False)
    note = db1.Column(db1.String(200))

    def __repr__(self):
        return f"Expense('{self.amount}', '{self.category}')"

class User(db1.Model):
    __bind_key__ = 'secondary'
    id = db1.Column(db1.Integer, primary_key=True)
    name = db1.Column(db1.String(50), nullable=False)
    email = db1.Column(db1.String(150), unique=True)
    password = db1.Column(db1.String(200), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(self.password.encode('utf-8'), password.encode('utf-8'))

with app.app_context():
    db1.create_all()

def create_3d_pie_chart(expenses):
    category_totals = {}

    if len(expenses) == 0:
        return None

    for expense in expenses:
        if expense.category in category_totals:
            category_totals[expense.category] += expense.amount
        else:
            category_totals[expense.category] = expense.amount

    labels = list(category_totals.keys())
    sizes = list(category_totals.values())

    colors = ['#3f3f3f', '#2f2f2f', '#202020', '#ffcc99', '#c2c2f0']

    fig, ax = plt.subplots(figsize=(8, 6))

    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=0, colors=colors, shadow=True, wedgeprops={'edgecolor': 'black'})

    ax.axis('equal')

    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)

    chart_url = base64.b64encode(img.getvalue()).decode('utf8')
    return chart_url

@app.route('/', methods=['POST', 'GET'])
def home():
    expenses = Expense.query.all()

    pie_chart_url = create_3d_pie_chart(expenses)

    return render_template('index.html', expenses=expenses, pie_chart_url=pie_chart_url)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            return render_template('register.html', error="Email already exists")

        new_user = User(name=name, email=email, password=password)
        db1.session.add(new_user)
        db1.session.commit()

        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['name'] = user.name
            return redirect('/')
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('name', None)
    return redirect('/login')

@app.route('/add', methods=['POST', 'GET'])
def add_expense():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        note = request.form['note']
        new_expense = Expense(amount=amount, category=category, note=note)
        db1.session.add(new_expense)
        db1.session.commit()

    return render_template('add.html', expenses=Expense.query.all())

if __name__ == '__main__':
    app.run(debug=True)
