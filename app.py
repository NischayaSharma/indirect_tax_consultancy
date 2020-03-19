from flask import Flask,render_template,redirect,url_for, request
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField, TextAreaField, SubmitField
from wtforms.validators import InputRequired,Email,Length, DataRequired
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user


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
    query = db.Column(db.Text)
    reply = db.Column(db.Text)
    asked_timestamp = db.Column(db.String(10))
    reply_timestamp = db.Column(db.String(10))

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

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


if __name__ == "__main__":
    app.run(debug=True)
