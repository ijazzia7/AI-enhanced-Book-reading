from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from DBmodel import db, User

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        age = request.form['age']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect(url_for('auth.register'))

        new_user = User(username=username, name=name, age=int(age))
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful. Please log in.")
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['username'] = username
            session['name'] = user.name
            flash("Login successful.")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.")
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('auth.login'))
