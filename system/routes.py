from flask import Flask, render_template, flash, redirect, url_for
from system.forms import RegistrationForm,LoginForm
from system import app

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register',methods=['GET',"POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account Created for {form.username.data}',category='success')
        return redirect(url_for('home'))
    return render_template('register.html',form=form,title='Register')


@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data =='krv111204@gmail.com' and form.password.data == 'pass':
            flash(f'{form.email.data} has logged in','success')
            return redirect(url_for('home'))
        else:
            flash(f'Wrong email id or password','danger')
            return redirect(url_for('login'))
    return render_template('login.html',form=form,title='Login')