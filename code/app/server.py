import hashlib
from flask import Flask, jsonify, request, render_template, g, redirect, Response, session
from transaction import *
from multiprocessing import Process
from database_objects import *
from database_methods import *
import database_methods 
from sqlalchemy import *
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker


app = Flask(__name__)
app.secret_key = '\n\x1f\xe9(\xf0DdG~\xd4\x863\xa0\x10\x1e\xbaF\x10\x16\x7f(\x06\xb7/'


@app.route('/')
def hello_world():
    if 'username' not in session:
        return redirect('/login')
    return redirect('/home')


def create_transaction(quantity, username):
    # insert new transaction record and grab generated id
    new_id = insertNewTransaction(quantity, username)
    # spin up new process to execute the transaction over time
    transaction_executer = TransactionExecuter(quantity, username, new_id)
    p = Process(target=transaction_executer.execute_transaction)
    p.start()


@app.route('/home', methods=['GET', 'POST'])
def transaction():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['quantity'] == '' or 'quantity' not in request.form:
            context = dict(error_message = "No quantity given")
            return render_template("home.html", username=session['username'], **context)
        # call function to execute the transaction
        create_transaction(float(request.form['quantity']), session['username'])
    return render_template("home.html", username=session['username'])


@app.route('/track_order', methods=['GET'])
def track_order():
    if 'username' not in session:
        return redirect('/login')
    username = session['username']
    # get list of all active trades for this user
    trade_list = getActiveTransactionList(username)
    return render_template('active-list.html', transactions=trade_list)


@app.route('/change', methods=['GET', 'POST'])
def change():
    if request.method == 'POST':
        if request.form['username'] == '' or 'username' not in request.form:
            context = dict(error_message = "No username given")
            return render_template("change.html", **context)
        if request.form['password'] == '' or 'password' not in request.form:
            context = dict(error_message = "No password given")
            return render_template("change.html", **context)
        if request.form['password_conf'] != request.form['new_password'] or\
                        'new_password' not in request.form:
            context = dict(error_message = "Passwords must match")
            return render_template("change.html", **context)
        username = request.form['username'].strip()
        oldpasshash = hashlib.md5(request.form['password']).hexdigest()
        newpasshash = hashlib.md5(request.form['new_password']).hexdigest()
        # get the user object from the database
        user = getUser(username)
        hashfound = user.password
        # make sure old password is valid
        if hashfound == None or hashfound != oldpasshash:
            context = dict(error_message = "Incorrect username or password")
            return render_template("change.html", **context)
        # change the users password to the new passhash
        updateUserPassword(username, newpasshash)
        return redirect('/')
    return render_template("change.html")


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        if request.form['username'] == '' or 'username' not in request.form:
            context = dict(error_message = "No username given")
            return render_template("create.html", **context)
        if request.form['password'] == '' or 'password' not in request.form:
            context = dict(error_message = "No password given")
            return render_template("create.html", **context)
        if request.form['password_conf'] != request.form['password'] or\
                        'password' not in request.form:
            context = dict(error_message = "Passwords must match")
            return render_template("create.html", **context)
        username = request.form['username'].strip()
        passhash = hashlib.md5(request.form['password']).hexdigest()
        # get the user object from the database
        user = getUser(username)
        if user != None:
            context = dict(error_message = "User name already exists")
            return render_template("create.html", **context)
        # insert new user record into the database
        insertNewUser(username, passhash)
        return redirect('/')
    return render_template("create.html")


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == '' or 'username' not in request.form:
            context = dict(error_message = "No username given")
            return render_template("login.html", **context)
        username = request.form['username']
        if request.form['password'] == '' or 'password' not in request.form:
            context = dict(error_message = "No password given")
            return render_template("login.html", **context)
        user = getUser(username)
        if user == None:
            return render_template('login.html', error="Incorrect username")
        passhash = user.password
        if passhash == None:
            return render_template('login.html', error="Incorrect username or password")
        password = request.form['password']
        if passhash != hashlib.md5(password).hexdigest():
            return render_template('login.html', error="Incorrect password")
        session['username'] = request.form['username']
        return redirect('/')
    return render_template('login.html')


if __name__ == '__main__':
    DATABASE_URI = "postgresql://localhost/master_4156_database"
    database_methods.engine = create_engine(DATABASE_URI)
    database_methods.Session = sessionmaker(bind=database_methods.engine)
    

    createSchema()
    app.run()
