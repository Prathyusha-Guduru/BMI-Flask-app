#########################################
### importing 3rd party libraries   #####
#########################################


from operator import imod
from flask import Flask,redirect,url_for,flash,request
from flask_sqlalchemy import SQLAlchemy
import os
from flask_migrate import Migrate
from flask_login import LoginManager,UserMixin
from flask_login.utils import login_required,login_user,current_user,logout_user
from flask_wtf import FlaskForm
from flask_wtf.csrf import _FlaskFormCSRF
from wtforms import StringField,PasswordField,SubmitField
from wtforms.fields.core import IntegerField
from wtforms.validators import DataRequired,Email,EqualTo
from wtforms import ValidationError
from flask_wtf.file import FileField,FileAllowed
from flask_login import current_user
from flask import render_template
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash



#########################################
################## CONFIG    ############
#########################################


app = Flask(__name__)
app.config['SECRET_KEY'] = 'izzasecret'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Migrate(app,db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'





#########################################
################## DB MODELS ############
#########################################
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(user_id)
class User(db.Model,UserMixin):
	__tablename__ = 'users'

	id = db.Column(db.Integer,primary_key = True)
	profile_image = db.Column(db.String(20),nullable = False,default = 'default.jpg')
	email = db.Column(db.String(64),unique = True,index = True)
	username = db.Column(db.String(64),unique = True,index = True)
	password_hash = db.Column(db.String(128))
	height = db.Column(db.Integer,default = 0)
	weight = db.Column(db.Integer,default = 0)

	def __init__(self,email,username,password,height,weight):
		self.email = email
		self.username = username
		self.password_hash = generate_password_hash(password)
		self.height = height
		self.weight = weight
	def check_password(self,password):
		return check_password_hash(self.password_hash,password)

	def getBMI(self,weight,height):
		bmi = weight / (height/100)**2
		return bmi

	def __repr__(self):
		return f"Username is {self.username}"


#########################################
################## FORMS ################
#########################################

class LoginForm(FlaskForm):
	email = StringField('Email',validators=[DataRequired(),Email()])
	password = PasswordField('Password',validators=[DataRequired()])
	submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
	email = StringField('Email',validators=[DataRequired(),Email()])
	username = StringField('Username',validators=[DataRequired()])
	password = PasswordField('Password',validators=[DataRequired(),EqualTo('pass_confirm',message='Passwords must match')])
	pass_confirm = PasswordField('Conifirm Password',validators=[DataRequired()])
	height = IntegerField('Height',validators=[DataRequired()])
	weight = IntegerField('Weight',validators=[DataRequired()])
	submit = SubmitField('Register')

	def check_email(self,field):
		if User.query.filter_by(email = field.data).first():
			raise ValidationError('Email has been registered already ')
	
	def check_username(self,field):
		if User.query.filter_by(username = field.data).first():
			raise ValidationError('Username has been registered already ')

	
class UpdateUserForm(FlaskForm):

	
	email = StringField('Email',validators=[DataRequired(),Email()])
	username = StringField('Username',validators=[DataRequired()])
	height = IntegerField('Updated height',validators=[DataRequired()])
	weight = IntegerField('Updated weight',validators=[DataRequired()])
	submit = SubmitField('Update')
	def check_email(self,field):
		if User.query.filter_by(email = field.data).first():
			raise ValidationError('Email has been registered already ')
	
	def check_username(self,field):
		if User.query.filter_by(username = field.data).first():
			raise ValidationError('Username has been registered already ')




#########################################
################## VIEWS ################
#########################################

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/register',methods = ['GET','POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
			user = User(email = form.email.data,username=form.username.data,password=form.password.data,weight = form.weight.data,height = form.height.data)
			db.session.add(user)
			db.session.commit()
			flash("Thanks for registration")
			return redirect(url_for('login'))
	return render_template('register.html',form = form)

@app.route('/login',methods = ['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()

		if user.check_password(form.password.data) and user is not None:
			login_user(user)
			flash('Log In Success')

			next = request.args.get('next')
			print(current_user.username)
			# if next == None or not next[0] == '/0':
			# 	next = url_for('account')
			return redirect(url_for('account'))
	return render_template('login.html',form= form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/account',methods = ['GET','POST'])
def account():
	form = UpdateUserForm()
	if form.validate_on_submit():

		# if form.username.data:
		# 	username= current_user.username
		# 	# pic = add_profile(form.picture.data,username)
		# 	# current_user.profile_image = pic

		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('User account updated')
		return redirect(url_for('account'))

	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	bmi = current_user.weight / (current_user.height/100)**2
	# profile_image = url_for('static',filename = 'profile_pics/' + current_user.profile_image)
	# print(f"Path to the profile image : {profile_image} ")

	return render_template('account.html',current_user = current_user,form = form,bmi = bmi)





