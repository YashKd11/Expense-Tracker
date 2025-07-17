from flask import Flask, render_template, request, redirect, flash, url_for #type: ignore
from flask_sqlalchemy import SQLAlchemy #type: ignore
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user #type: ignore
from werkzeug.security import generate_password_hash, check_password_hash #type: ignore
from datetime import date, timedelta, datetime


app = Flask(__name__)
app.secret_key = 'jajantaramMamamantaram'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category = db.Column(db.String(50), nullable=False)
    note = db.Column(db.String(200))    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Expense('{self.amount}', '{self.category}')"
    
    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'amount': self.amount,
            'date':self.date.strftime('%d-%m-%Y')
        }

class User(UserMixin ,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200), nullable=False)
    expenses = db.relationship('Expense', backref='user', lazy=True)

def dash_func(expenses):
    category_totals = {}
    for e in expenses:
        cat = e['category']
        amt = e['amount']

        category_totals[cat] = category_totals.get(cat, 0) + amt
    return category_totals


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/logout',methods=['POST','GET'])
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invlaid Email or password')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
    timeSpan = request.args.get('range', '')
    query = Expense.query.filter_by(user_id=current_user.id)
    today = date.today()

    if timeSpan == 'today':
        start = datetime.combine(today, datetime.min.time())
        end = datetime.combine(today, datetime.max.time())
        query = query.filter(Expense.date >= start, Expense.date <= end)

    elif timeSpan == 'week':
        week_ago = today - timedelta(days=7)
        query = query.filter(Expense.date >= week_ago)

    elif timeSpan == 'month':
        month_ago = today - timedelta(days=30)
        query = query.filter(Expense.date >= month_ago)

    data = [e.to_dict() for e in query]
    category_totals = dash_func(data)

    if category_totals:
        max_key = max(category_totals, key=category_totals.get)
        max_val = category_totals[max_key]
    else:
        max_key = "N/A"
        max_val = 0

    return render_template('dashboard.html',
                           category=max_key,
                           value=max_val,
                           data=data,
                           selected_range=timeSpan)


@app.route('/add', methods=['POST', 'GET'])
@login_required
def add_expense():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        note = request.form['note']
        new_expense = Expense(amount=amount, category=category, note=note, user_id=current_user.id)
        db.session.add(new_expense)
        db.session.commit()

    return render_template('add.html')

@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(name=username).first():
            flash("User Already Exists ")
            return render_template('login.html')
        hash = generate_password_hash(password)
        new_user = User(name=username, email=email, password=hash)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration Successfull ")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html')











if __name__ == '__main__':
    app.run(debug=True)
