import hashlib
from flask import Flask, jsonify, request, render_template, g, redirect, Response, session
from transaction import *
from multiprocessing import Process
from database import *


app = Flask(__name__)
app.secret_key = '\n\x1f\xe9(\xf0DdG~\xd4\x863\xa0\x10\x1e\xbaF\x10\x16\x7f(\x06\xb7/'


@app.route('/')
def hello_world():
    if 'username' not in session:
        return redirect('/login')
    return redirect('/home')


def create_transaction(quantity, username):
    dbsession = Session()
    max_id = dbsession.query(func.max(Transactions.id)).filter_by(username=username).first()[0]
    if max_id == None:
        new_id = 0
    else:
        new_id = max_id + 1

    new_transaction = Transactions(username=username, id=new_id, completed=0, finished=False)
    dbsession.add(new_transaction)
    dbsession.commit()
    dbsession.close()

    p = Process(target=execute_transaction, args=(quantity, username, new_id,))
    p.start()

    return new_id


@app.route('/home', methods=['GET', 'POST'])
def transaction():
    if 'username' not in session:
        return redirect('/login')

    trans_id = -1
    if request.method == 'POST':
        if request.form['quantity'] == '' or 'quantity' not in request.form:
            context = dict(error_message = "No quantity given")
            return render_template("home.html", username=session['username'], **context)
        # execute a transaction
        #p = Process(target=execute_transaction, args=(float(request.form['quantity']),))
        #p.start()
        trans_id = create_transaction(float(request.form['quantity']), session['username'])
        # execute_transaction(float(request.form['quantity']))
    return render_template("home.html", username=session['username'], id=trans_id)


@app.route('/track_order', methods=['GET'])
def track_order():
    if 'username' not in session:
        return redirect('/login')

    order_id = request.args['id']
    username = session['username']

    if int(order_id) == -1:
        return jsonify(completed=0, trans_completed=True)

    dbsession = Session()
    trans = dbsession.query(Transactions).filter_by(username=username, id=order_id).first()
    num_completed = trans.completed
    finished = trans.finished
    dbsession.close()

    print num_completed

    return jsonify(completed=num_completed, trans_finished=finished)


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

        dbsession = Session()
        user = dbsession.query(UserPass).filter_by(username=username).first()
        hashfound = user.password

        if hashfound == None or hashfound != oldpasshash:
            dbsession.close()
            context = dict(error_message = "Incorrect username or password")
            return render_template("change.html", **context)

        user.password = newpasshash
        dbsession.commit()
        dbsession.close()

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

        dbsession = Session()
        user = dbsession.query(UserPass).filter_by(username=username).first()

        if user != None:
            dbsession.close()
            context = dict(error_message = "User already exists")
            return render_template("create.html", **context)

        new_user = UserPass(username=username, password=passhash)
        dbsession.add(new_user)
        dbsession.commit()
        dbsession.close()

        return redirect('/')

    return render_template("create.html")


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == '' or 'username' not in request.form:
            context = dict(error_message = "No username given")
            return render_template("login.html", **context)
        if request.form['password'] == '' or 'password' not in request.form:
            context = dict(error_message = "No password given")
            return render_template("login.html", **context)
        dbsession = Session()
        user = dbsession.query(UserPass).filter_by(username=request.form['username']).first()
        dbsession.close()
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
    # create datbase schema if not exists
    # TODO
    app.run()
