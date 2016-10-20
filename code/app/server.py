import hashlib
from sqlalchemy import *
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from flask import Flask, request, render_template, g, redirect, Response, session
from transaction import *
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)

DATABASE_URI = "postgresql://localhost/users"
engine = create_engine(DATABASE_URI)
Base = declarative_base()
Session = sessionmaker(bind=engine)

app.secret_key = '\n\x1f\xe9(\xf0DdG~\xd4\x863\xa0\x10\x1e\xbaF\x10\x16\x7f(\x06\xb7/'

class UserPass(Base):
    __tablename__ = 'userpass'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)

    def __repr__(self):
        return "<UserPass(username='%s', password='%s')>" % (self.username, self.password)

@app.route('/')
def hello_world():
    if 'username' not in session:
        return redirect('/login')
    return redirect('/home')


@app.route('/home', methods=['GET', 'POST'])
def transaction():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['quantity'] == '' or 'quantity' not in request.form:
            context = dict(error_message = "No quantity given")
            return render_template("home.html", username=session['username'], **context)
        # execute a transaction
        execute_transaction(float(request.form['quantity']))
    return render_template("home.html", username=session['username'])


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

        g.conn = engine.connect()

        cursor = g.conn.execute("SELECT * FROM userpass WHERE username=%s", username)
        hashfound = cursor.first()[1]

        if hashfound == None or hashfound != oldpasshash:
            context = dict(error_message = "Incorrect username or password")
            return render_template("change.html", **context)

        g.conn.execute("UPDATE userpass SET password = %s WHERE username = %s", newpasshash, username)
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

        g.conn = engine.connect()

        cursor = g.conn.execute("SELECT * FROM userpass WHERE username=%s", username)

        if cursor.first() != None:
            context = dict(error_message = "User already exists")
            return render_template("create.html", **context)

        new_user = UserPass(username=username, password=passhash)
        session = Session()
        session.add(new_user)
        session.commit()
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
        g.conn = engine.connect()
        cursor = g.conn.execute("SELECT password FROM userpass WHERE username=%s",request.form['username'])
        passhash = cursor.first()[0]
        if passhash == None:
            return render_template('login.html', error="Incorrect username or password")
        password = request.form['password']
        if passhash != hashlib.md5(password).hexdigest():
            return render_template('login.html', error="Incorrect password")

        session['username'] = request.form['username']
        return redirect('/')

    return render_template('login.html')


if __name__ == '__main__':
    # create the schema if not exists
    Base.metadata.create_all(engine)
    app.run()
