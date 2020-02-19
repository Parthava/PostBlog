from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, current_user, UserMixin #############################

app=Flask(__name__)
app.secret_key = 'random string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reg.db'
dbreg=SQLAlchemy(app)
bcrypt=Bcrypt()

login_manager=LoginManager(app) ###########################

class reg(dbreg.Model, UserMixin):
	id=dbreg.Column(dbreg.Integer, primary_key=True)
	username=dbreg.Column(dbreg.String(50), nullable=False)
	email=dbreg.Column(dbreg.String(40), nullable=False)
	password=dbreg.Column(dbreg.String(100), nullable=False)
	fburl=dbreg.Column(dbreg.String(30), nullable=True)
	secques=dbreg.Column(dbreg.String(30), nullable=True)
	bio=dbreg.Column(dbreg.String(30), nullable=True)
	profilepic=dbreg.Column(dbreg.String(30), nullable=True)
	date=dbreg.Column(dbreg.DateTime, nullable=False, default=datetime.utcnow)

	def __repr__(self):
		return 'User id: ' + str(self.id)

class PostBlog(dbreg.Model, UserMixin):
	id=dbreg.Column(dbreg.Integer, primary_key=True)
	regusername=dbreg.Column(dbreg.String(50), nullable=False)
	title=dbreg.Column(dbreg.String(100), nullable=False)
	content=dbreg.Column(dbreg.Text, nullable=False)
	author=dbreg.Column(dbreg.String(20), nullable=False, default='N/A')
	date=dbreg.Column(dbreg.DateTime, nullable=False, default=datetime.utcnow)

	def __repr__(self):
		return 'Blog Post' + str(self.id)

######################################################
@login_manager.user_loader
def load_user(id):
	return reg.query.get(id)
######################################################

@app.route('/')
@app.route('/index')
def index():
	all_posts=PostBlog.query.all()
	return render_template('index.html', datas=all_posts)

'''@app.route('/home/newpost')
def newpost():
	return render_template('newpost.html')'''

@app.route('/index/newpost', methods=['GET','POST'])
def addnewpost():
	if current_user.is_authenticated:
		if request.method=='POST':
			post_username=current_user.username
			post_title=request.form['title']
			post_content=request.form['content']
			#post_author=current_user.fburl
			new_post=PostBlog(regusername=post_username, title=post_title, content=post_content)
			dbreg.session.add(new_post)
			dbreg.session.commit()
			flash("Your post has been added")
			return redirect(url_for('index'))

		else:
			return render_template('newpost.html')
	else:
		return redirect(url_for('index'))

'''@app.route('/index/account') # User profile
def account():
	if current_user.is_authenticated:
		searchuser=current_user.username
		data=PostBlog.query.filter_by(regusername=searchuser).all()
		return render_template('account.html', datas=data)
	else:
		return redirect(url_for('index'))'''

@app.route('/index/account/<string:pusrname>')
def account(pusrname):
	if current_user.is_authenticated:
		data=PostBlog.query.filter_by(regusername=pusrname).all()
		return render_template('account.html', datas=data)
	else:
		return redirect(url_for('index'))

@app.route('/account/delete/<int:id>') # User profile
def delete(id):
	if current_user.is_authenticated:
		data=PostBlog.query.get_or_404(id)
		dbreg.session.delete(data)
		dbreg.session.commit()
		path='/index/account/' + current_user.username
		return redirect(path)
	else:
		return redirect(url_for('index'))

@app.route('/account/edit/<int:id>', methods=['GET','POST']) # User profile
def edit(id):
	if current_user.is_authenticated:
		data=PostBlog.query.get_or_404(id)
		if request.method=='POST':
			data.title=request.form['title']
			data.content=request.form['content']
			#data.author=request.form['author']
			dbreg.session.commit()
			path='/index/account/' + current_user.username
			return redirect(path)
		else:
			return render_template('edit.html', datas=data)

	else:
		return redirect(url_for('index'))

'''@app.route('/index/profile/<string:name>')
def profile(name):
	if current_user.is_authenticated:
		searchuser=current_user.username
		data=reg.query.filter_by(username=searchuser).all()
		return render_template('profile.html', datas=data)
	else:
		return redirect(url_for('index'))'''
@app.route('/index/profile/<string:usrname>')
def profile(usrname):
	if current_user.is_authenticated:
		data=reg.query.filter_by(username=usrname).all()
		return render_template('profile.html', datas=data)
	else:
		return redirect(url_for('index'))

@app.route('/profile/edit/<int:id>', methods=['GET','POST'])
def prfledit(id):
	if current_user.is_authenticated:
		data=reg.query.get_or_404(id)
		if request.method=='POST':
			data.username=request.form['username']
			data.email=request.form['email']
			data.bio=request.form['bio']
			data.fburl=request.form['fburl']
			data.secques=request.form['secques']
			dbreg.session.commit()
			path='/index/profile/' + current_user.username
			return redirect(path)
		else:
			return render_template('prfledit.html', datas=data)

	else:
		return redirect(url_for('index'))

@app.route('/reg', methods=['GET','POST'])
def register():
	if current_user.is_authenticated:     
		return redirect(url_for('index')) ####################################################

	if request.method=='POST':
		reg_username=request.form['username']
		reg_email=request.form['email']
		reg_password=request.form['password']
		reg_bio=request.form['bio']
		reg_fburl=request.form['fburl']
		reg_secques=request.form['secques']
		hashed_pw=bcrypt.generate_password_hash(reg_password).decode('utf-8')
		new_user=reg(username=reg_username, email=reg_email, password=hashed_pw, bio=reg_bio, fburl=reg_fburl, secques=reg_secques)
		if(reg.query.filter_by(username=reg_username).all()):
			flash("Username is already taken. Please choose another one")
			return redirect('/reg')
		else:
			dbreg.session.add(new_user)
			dbreg.session.commit()
			flash('Your account has been created')
			return redirect(url_for('sign_in'))

	else:
		return render_template('reg.html')

@app.route('/login', methods=['GET','POST'])
def sign_in():
	if current_user.is_authenticated:
		return redirect(url_for('index')) ####################################################
	if request.method=='POST':
		ck_username=request.form['username']
		ck_password=request.form['password']
		if(reg.query.filter_by(username=ck_username).first()):
			db_username=reg.query.filter_by(username=ck_username).first()
			db_user_id=db_username.id
			db_password=reg.query.get(db_user_id).password
			if(bcrypt.check_password_hash(db_password,ck_password)):
				login_user(db_username)
				return redirect(url_for('index'))
			else:
				flash("Login Unsuccessful! Please check Username and Password")
				return redirect(url_for('sign_in'))
		else:
			flash("Login Unsuccessful! Username not valid")
			return redirect(url_for('register'))

	else:
		return render_template('login.html')

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

if __name__ == "__main__":
	app.run(debug=True)