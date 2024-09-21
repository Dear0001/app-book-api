from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user
from .form import LoginForm
from app.models import *
from app.extensions import *

auth_bp = Blueprint('auth', __name__ )

@auth_bp.route('/login')
def show_login():
    form = LoginForm()
    return render_template('login.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('main.index'))
    
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password_hash, password):
        login_user(user, remember=remember)
        flash('Login successful', 'success')
        return redirect(url_for('main.profile'))
    else:
        flash('Invalid username or password. Please try again.', 'danger')
        return redirect(url_for('auth.show_login')) 

@auth_bp.route('/signup')
def signup():
    form = LoginForm()
    return render_template('signup.html', form=form)

@auth_bp.route('/signup', methods=['POST','GET'])
def signup_post():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    gender = request.form.get('gender')
    
    user = User.query.filter_by(username=username).first()
    email_exists = User.query.filter_by(email=email).first()
    
    if user:
        flash('Username already exists. Please choose a different one.', 'danger')
        return redirect(url_for('auth.signup'))
    if email_exists:
        flash('Email already exists. Please choose a different one.', 'danger')
        return redirect(url_for('auth.signup'))
    
    new_user = User(username=username, 
                    email=email,
                    password_hash=generate_password_hash(password, method='pbkdf2:sha256'),
                    gender=gender)
    
    new_profile = Profile(username=username, 
                    email=email,
                    password_hash=generate_password_hash(password, method='pbkdf2:sha256'),
                    gender=gender)
    
    db.session.add(new_user)
    db.session.add(new_profile)
    db.session.commit()
    
    # Fetch the user from the database after committing the session
    user = User.query.filter_by(username=username).first()
    login_user(user)
    
    return redirect(url_for('main.profile'))
@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.show_login'))

@login_manager.user_loader
def load_user(username):
    return User.query.get(username)
