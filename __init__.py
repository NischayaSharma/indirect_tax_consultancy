import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, json
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, Email, Length, DataRequired
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from flask.json import jsonify
from sqlalchemy_serializer import SerializerMixin
import smtplib


app = Flask(__name__)
app.config['SECRET_KEY'] = "lolly"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'troubleshooter.xyz@gmail.com'
app.config['MAIL_PASSWORD'] = 'pass1911'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
jsdata = ""
isAdmin = False


class User(UserMixin, db.Model, SerializerMixin):
    __tablename__ = "user"
    serialize_rules = ('-doubt.user', '-subqueries.user',
                       '-doubt.subqueries.user', '-subqueries.doubt')
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    isAdmin = db.Column(db.Integer, default=0)

    doubt = db.relationship('Doubts', backref='user')
    subqueries = db.relationship('SubQueries', backref='user')


class Doubts(db.Model, SerializerMixin):
    __tablename__ = "doubts"
    serialize_rules = ('-subqueries.doubt',)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey("user.id"))
    userqrynum = db.Column(db.Integer)
    title = db.Column(db.Text)
    query = db.Column(db.Text)
    reply = db.Column(db.Text)
    upload = db.Column(db.Text)
    asked_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    reply_timestamp = db.Column(db.DateTime)

    subqueries = db.relationship('SubQueries', backref='doubt')


class SubQueries(db.Model, SerializerMixin):
    __tablename__ = "subqueries"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey("user.id"))
    qryid = db.Column(db.Integer, db.ForeignKey("doubts.id"))
    userqrynum = db.Column(db.Integer)
    query = db.Column(db.Text)
    title = db.Column(db.Text)
    reply = db.Column(db.Text)
    upload = db.Column(db.Text)
    asked_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    reply_timestamp = db.Column(db.DateTime)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.context_processor
def loggedn_in_user():
    return dict(logged_in=current_user.is_authenticated)


@app.context_processor
def inject_user():
    return dict(user=current_user)


@app.route('/')
def index():
    return render_template('index2.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        global isAdmin
        user = User.query.filter_by(username=request.form['username']).first()
        if user:
            if check_password_hash(user.password, request.form['password']):
                login_user(user)
                if (user.isAdmin == 1):
                    isAdmin = True

                print(isAdmin)
                return redirect(url_for('dashboard'))
            return '<h1>Invalid Pass</h1>'
        return render_template('signup.html')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        hashed_password = generate_password_hash(
            request.form['password'], method='sha256')
        new_user = User(username=request.form['username'], email=request.form['email'],
                        password=hashed_password, isAdmin=1 if request.form['username'] == "sharad" else 0)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.isAdmin == 1:
        return render_template('admin_dashboard.html')
    else:
        return render_template('dashboard.html', queries=current_user.doubt)


@app.route('/aboutus')
def aboutus():
    print(current_user)
    return render_template('aboutus.html', loggedin=current_user.is_authenticated)


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
        print(request.files)
        path = ""
        if 'uploaded_file' in request.files:
            f = request.files['uploaded_file']
            if f.filename != '':
                if not os.path.exists(os.path.join(os.path.dirname(__file__), "uploads", str(current_user.username)+"."+tle)):
                    os.makedirs(os.path.join(os.path.dirname(
                        __file__), "uploads", str(current_user.username)+"."+tle))
                path = os.path.join(os.path.dirname(__file__), "uploads", str(
                    current_user.username)+"."+tle, secure_filename(f.filename))
                f.save(path)
        usrqry = len(current_user.doubt)+1
        new_doubt = Doubts(user=current_user, title=tle, query=qry,
                           userqrynum=usrqry, upload=path, asked_timestamp=datetime.utcnow())
        db.session.add(new_doubt)
        db.session.commit()
        subject = str(current_user.id)+"."+str(usrqry)+": "+str(tle)
        body = str(qry)+"\n\nBy "+str(current_user.username)+"."
        send_mail(subject, body)
        return redirect(url_for('dashboard'))
    return render_template('askquestion.html')


@app.route('/myquestions', methods=['GET', 'POST'])
@login_required
def myquestions():
    if current_user.isAdmin == 1:
        global jsdata
        queries = []
        users = User.query.all()
        for user in users:
            print(user.doubt)
            for dbt in user.doubt:
                queries.append(dbt)
        print(queries)
        print(request.method)
        if request.method == "POST":
            qry = queries[int(jsdata)-1]
            print(qry.reply)
            if qry.reply == "" or qry.reply is None:
                qry.reply = request.form['qry_reply']
                qry.reply_timestamp = datetime.utcnow()
            else:
                subqry = qry.subqueries[len(qry.subqueries)-1]
                subqry.reply = request.form['qry_reply']
                subqry.reply_timestamp = datetime.utcnow()
            db.session.commit()
            usr = User.query.filter_by(id=qry.userid).first()
            subject = "Reply To Query: "+str(qry.title)
            body = str(request.form['qry_reply'])+"\n\nBy Admin"
            send_mail(subject,body,usr.email)
            return redirect(url_for('dashboard'))
        return render_template('adminquestions.html', queries=queries)
    else:
        print(current_user.doubt)
        return render_template('myquestions.html', queries=current_user.doubt)


@app.route('/postmethod', methods=['POST'])
def get_javascript_data():
    try:
        global jsdata
        jsdata = request.get_json()
        jsonStr = current_user.doubt[int(jsdata)-1].to_dict()
        print(jsonStr)
        return jsonify(jsonStr)
    except ValueError:
        return jsonify('OK')


@app.route('/admindata', methods=['POST'])
def admin_js():
    try:
        global jsdata
        jsdata = request.get_json()
        queries = []
        users = User.query.all()
        for user in users:
            print(user.doubt)
            for dbt in user.doubt:
                queries.append(dbt)
        print(queries)
        print(jsdata)
        jsonStr = queries[int(jsdata)-1].to_dict()
        print(jsonStr)
        return jsonify(jsonStr)
    except ValueError:
        return jsonify('OK')


@app.route('/askfurtherquestion', methods=['GET', 'POST'])
@login_required
def askfurtherquestion():
    global jsdata
    print(jsdata)
    if request.method == 'POST':
        tle = request.form['qry_title']
        qry = request.form['content']
        print(request.files)
        path = ""
        if 'uploaded_file' in request.files:
            f = request.files['uploaded_file']
            if f.filename != '':
                if not os.path.exists(os.path.join(os.path.dirname(__file__), "uploads", "user", str(current_user.username)+"."+tle)):
                    os.makedirs(os.path.join(os.path.dirname(
                        __file__), "uploads", "user", str(current_user.username)+"."+tle))
                path = os.path.join(os.path.dirname(__file__), "uploads", "user", str(
                    current_user.username)+"."+tle, secure_filename(f.filename))
                f.save(path)
        usrqry = len(current_user.doubt[int(jsdata)-1].subqueries)+1
        new_doubt = SubQueries(user=current_user, title=tle, query=qry, userqrynum=usrqry,
                               upload=path, asked_timestamp=datetime.utcnow(), doubt=current_user.doubt[int(jsdata)-1])
        db.session.add(new_doubt)
        db.session.commit()
        subject = str(current_user.id)+"."+str(
            current_user.doubt[int(jsdata)-1].userqrynum)+""+str(usrqry)+": "+str(tle)
        body = str(qry)+"\n\nBy "+str(current_user.username)+"."
        send_mail(subject, body)
        return redirect(url_for('dashboard'))
    return render_template('askfurtherquestion.html')


def send_mail(subject, body, recipient="troubleshooter.xyz@gmail.com"):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login('tax.troubleshooterr@gmail.com', 'dbcsomrfzzhzdciw')
    msg = "Subject:"+subject+"\n\n"+body
    server.sendmail('tax.troubleshooterr@gmail.com', recipient, msg)
    server.quit()


if __name__ == "__main__":
    app.run(debug=True)
