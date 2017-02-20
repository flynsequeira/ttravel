import os
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, send_from_directory
from werkzeug import secure_filename
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, BlogPost
from flask import session as login_session
import random
import string
from wtforms import Form, BooleanField, TextField, PasswordField, validators, RadioField, DateField, StringField
from wtforms.widgets import TextArea
from passlib.hash import sha256_crypt
from datetime import datetime, date

PROJ_FOLDER = os.getcwd()
UPLOAD_FOLDER = PROJ_FOLDER+'/blogImages'
# UPLOAD_FOLDER = '/Users/flyn/documents/TravelProj/blogImages'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "n$v0a_h)3t591@mw#@i6&qkv6#n+b%+)+88)5t7@46v+(=f$f&"

#Connecting to database
engine = create_engine('sqlite:///travellerdata.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#PRETTY LOOKIN DATE TIME
def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(second_diff / 60) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(second_diff / 3600) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff / 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff / 30) + " months ago"
    return str(day_diff / 365) + " years ago"

@app.route('/')
@app.route('/index')
@app.route('/home')
def home():
    posts = session.query(BlogPost).order_by(desc(BlogPost.id)).limit(3)
    bloggers = session.query(User)
    if login_session:
        name=login_session['user']
        logged_user = session.query(User).filter_by(email=login_session['email']).first()
        return render_template('home.html', logged_user=logged_user, posts=posts, bloggers=bloggers)
    return render_template('home.html', posts=posts, bloggers=bloggers)

@app.route('/plan_trip')
def plan_trip():
	if login_session:
		name=login_session['user']
		user = session.query(User).filter_by(email=login_session['email']).first()


@app.route('/blog')
def blog_posts():
	bloggers = session.query(User)
	if login_session:
		name=login_session['user']
		logged_user = session.query(User).filter_by(email=login_session['email']).first()
		posts = session.query(BlogPost).order_by((BlogPost.id))
		return render_template('blogposts.html', posts=posts, name=name, logged_user=logged_user, bloggers=bloggers)
	else:
		posts = session.query(BlogPost).order_by(desc(BlogPost.id))
		return render_template('blogposts.html', posts=posts, bloggers=bloggers)

@app.route('/blog_pic/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

#Retrieve
@app.route('/blog/<int:blog_id>')
def post(blog_id):
	post=session.query(BlogPost).filter_by(id=blog_id).one()
	blogger = session.query(User).filter_by(id=post.user_id).one()
	filename = post.filename
	if login_session:
		logged_user = session.query(User).filter_by(email=login_session['email']).first()
		return render_template('post.html',post=post, blogger=blogger, logged_user=logged_user)
	else:
		return render_template('post.html',post=post, blogger=blogger)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/blog/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        if login_session:
            file = request.files['file']
            logged_user = session.query(User).filter_by(email=login_session['email']).first()
            lastPost = session.query(BlogPost).order_by(BlogPost.id.desc()).first()
            if lastPost:
            	nextPostId=lastPost.id+1
            else:
            	nextPostId=1
            if file:
                
                filename = str(nextPostId)+secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                #ADD FILE NAME to BLOG_ID=X
                newPost = BlogPost(title=request.form['title'], description=request.form['description'], time=datetime.now(), user_id=logged_user.id, filename=filename)
                session.add(newPost)
                flash('New post about "%s"  was successfully created' % newPost.title)
                session.commit()
            

            return redirect(url_for('blog_posts'))
        else:
            return redirect(url_for('login'))
    else:
        if login_session:
        	logged_user = session.query(User).filter_by(email=login_session['email']).first()
        	return render_template('newpost.html', logged_user=logged_user)
        else:
        	flash(u'Invalid password provided', 'error')
        	return redirect(url_for('login'))


@app.route('/blog/<int:blog_id>/edit', methods=['GET', 'POST'])
def edit_post(blog_id):
    post=session.query(BlogPost).filter_by(id=blog_id).one()
    if login_session:
        logged_user = session.query(User).filter_by(email=login_session['email']).first()
        if post.user_id==logged_user.id:
            if request.method == 'POST':
                if request.form['title']:
                    post.title = request.form['title']
                if request.form['description']:
                    post.description = request.form['description']
                session.add(post)
                session.commit()
                return redirect(url_for('blog_posts'))
            else:
                return render_template('editpost.html', logged_user=logged_user)
    return redirect(url_for('home'))

@app.route('/blog/<int:blog_id>/delete')
def delete_post(blog_id):
    postToDelete=session.query(BlogPost).filter_by(id=blog_id).one()
    if login_session:
        user = session.query(User).filter_by(email=login_session['email']).first()
        if postToDelete.user_id==user.id:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], postToDelete.filename))
            session.delete(postToDelete)
            session.commit()
            return redirect(url_for('blog_posts'))
    return redirect(url_for('home'))

class Login(Form):
    email = TextField('Email', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    flash(u'Logged out', 'success')
    login_session.clear()
    return redirect(url_for("home"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        form = Login(request.form)
        if request.method == "POST" and form.validate():
            email = form.email.data
            password = form.password.data
            user=session.query(User).filter_by(email=email).first()
            if user:
                if sha256_crypt.verify(password,user.password):
                    login_session['logged_in'] = True
                    login_session['user']=user.name
                    login_session['email']=user.email
                    flash(u'successfully logged in', 'success')
                    return redirect(url_for("home"))
                flash(u'Invalid password provided', 'error')
                return render_template("login.html", form=form)
            else:
                flash(u'Your email is not register. <a href="{{url_for(UserRegistration)}}"> Click here </a> to register', 'error')
                return render_template("login.html", form=form)
        else:
            return render_template("login.html", form=form)
    except Exception as e:
        return(str(e))

class UserRegistration(Form):
    name = TextField('My name is...', [validators.Required(), validators.Length(min=2, max=30)])
    email = TextField('And my email...', [validators.Required(), validators.Length(min=6, max=50), validators.Regexp('(\w+@\w+(?:\.\w+))', flags=0, message='This isn\'t a valid email')])
    mobile = TextField('Here\'s my mobile number...', [validators.Required(), validators.Regexp('(\d{10})', flags=0, message='This isn\'t a valid number'), validators.Length(min=10, max=10, message='This isn\'t a valid number')])
    companion = TextField('The type of travel companion I\'d like to have...',validators=(validators.Required(), validators.Length(min=20, max=1000),), widget=TextArea())
    gender = RadioField('I am a...', validators=(validators.Required(),), choices=[('male','Guy'),('female','Girl')], coerce=unicode)
    profession = RadioField('Currently...', validators=(validators.Required(),), choices=[('student','studying'),('worker','working')], coerce=unicode)
    dob = DateField('I was born on...', format='%m/%d/%Y', validators=(validators.Required(message='This field is required or your format is wrong. If format is wrong, refer to the format below.'),))
    password = PasswordField('This is my secure password...', [validators.Required(), validators.EqualTo('confirm', message="Password must match"), validators.Length(min=8, max=24)])
    confirm = PasswordField('Repeat')

    accept_tos = BooleanField('I accept the Terms of Service')



@app.route('/register/user', methods=['GET', 'POST'])
def register_user():
    try:
        form = UserRegistration(request.form)
        if request.method == "POST" and form.validate():
            user = form.name.data
            email = form.email.data
            profession = form.profession.data
            dob = form.dob.data
            mobile = form.mobile.data
            gender = form.gender.data
            companion = form.companion.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            user_exists=session.query(User).filter_by(email=email).first()
            if user_exists:
                flash(u'The email is already taken. Please login with the email or choose another email', 'error')
                return render_template('registeruser.html', form=form)
            else:
                newUser = User(name=user, email=email, password = password, dob=dob, mobile=mobile, profession=profession, gender=gender, ttype=companion)
                session.add(newUser)
                flash(u'Thank You for registering, "%s"' % newUser.name, 'success')
                session.commit()
                login_session['logged_in'] = True
                login_session['user']=user
                login_session['email']=email
                return redirect(url_for('home'))
        else:
            return render_template("registeruser.html", form=form)

    except Exception as e:
        return(str(e))

# @app.route('/register/vendor')
# def register_vendor():
#     return 'register as vendor'

# @app.route('/register/guide')
# def register_guide():
#     return 'register as guide'

@app.route('/mapitout')
def map():
    return render_template("maps.html")

@app.route('/flights')
def flights():
    return render_template("flights.html")

@app.route('/hotels')
def hotels():
    return render_template("hotels.html")

@app.route('/homestays')
def homestays():
    return render_template("homestays.html")

@app.route('/houseboats')
def houseboats():
    return render_template("houseboats.html")

if __name__ == "__main__":
    app.run(debug=True)



