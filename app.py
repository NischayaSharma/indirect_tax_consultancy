from datetime import datetime
from flask import Flask,render_template,redirect,url_for, request
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField, TextAreaField, SubmitField
from wtforms.validators import InputRequired,Email,Length, DataRequired
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
import random,json

app=Flask(__name__)
app.config['SECRET_KEY']="lolly"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db=SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

    doubt = db.relationship('Doubts', backref='user')

class Doubts(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey("user.id"))
    userqrynum = db.Column(db.Integer)
    title = db.Column(db.Text)
    query = db.Column(db.Text)
    reply = db.Column(db.Text)
    upload = db.Column(db.Text)
    asked_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    reply_timestamp = db.Column(db.DateTime)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class loginform(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')


@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user= User.query.filter_by(username=request.form['username']).first()
        if user:
            if check_password_hash(user.password,request.form['password']):
                login_user(user)

                return redirect(url_for('dashboard'))
            return '<h1>Invalid Pass</h1>'
        return render_template('signup.html')
    return render_template('login.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        hashed_password=generate_password_hash(request.form['password'],method='sha256')
        new_user=User(username=request.form['username'],email=request.form['email'],password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard2.html',user=current_user,queries=current_user.doubt)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/askquestion', methods=['GET', 'POST'])
@login_required
def askquestion():
    if request.method == 'POST':
        tle = request.form['qry_title']
        qry = request.form['content']
        usrqry = len(current_user.doubt)+1
        new_doubt = Doubts(user=current_user, title=tle, query=qry, userqrynum=usrqry, upload="", asked_timestamp=datetime.utcnow())
        db.session.add(new_doubt)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('askquestion.html')


@app.route('/myquestions')
@login_required
def myquestions():
    return render_template('myquestions.html',queries=current_user.doubt)

@app.route('/')
def output():
	# serve index template
	return render_template('index.html', name='Joe')

@app.route('/receiver', methods = ['POST'])
def worker():
	# read json + reply
	data = request.get_json()
	result = ''

	for item in data:
		# loop over every row
		result += str(item['make']) + '\n'

	return result





if __name__ == "__main__":
    app.run(debug=True)
