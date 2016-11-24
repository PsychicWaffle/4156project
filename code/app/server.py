import hashlib
from flask import Flask, jsonify, request, render_template, g, redirect, Response, session
from transaction import *
import multiprocessing
from multiprocessing import Process
from database_objects import *
from database_methods import *
import database_methods 
from sqlalchemy import *
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from Queue import Queue
from threading import Thread
import datetime
import sys
import validity_checker


app = Flask(__name__)
app.secret_key = '\n\x1f\xe9(\xf0DdG~\xd4\x863\xa0\x10\x1e\xbaF\x10\x16\x7f(\x06\xb7/'

MAX_AGE = 12 * 60 * 60

def process_workload(q):
    while True:
        args = q.get()
        execute_transaction(args[0], args[1], args[2])
        q.task_done()

def execute_transaction(new_id, quantity, username):
    # insert new transaction record and grab generated id
    # spin up new process to execute the transaction over time
    transaction_executer = TransactionExecuter(quantity, username, new_id)
    transaction_executer.execute_transaction()

# Check for incomplete transctions each time the server is restarted
@app.before_first_request
def run_start_up_funcs():
   check_incomplete_transaction()

def check_incomplete_transaction():
    if 'username' not in session:
        return
    active_transactions = database_methods.getActiveTransactions(session['username'])
    for active_transaction in active_transactions:
        remaining_qty = active_transaction.qty_requested - active_transaction.qty_executed
        trans_id = active_transaction.id
        my_queue.put([trans_id, remaining_qty, session['username']])

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
        # call function to execute the transaction
        if (validity_checker.valid_order_parameters(request.form['quantity']) == False):
            context = dict(error_message = "Invalid parameters")
            return render_template("home.html", username=session['username'], **context)
        new_id = insertNewTransaction(float(request.form['quantity']), session['username'])
        my_queue.put([new_id, float(request.form['quantity']), session['username']])
    return render_template("home.html", username=session['username'])

@app.route('/track_order', methods=['GET'])
def track_order():
    if 'username' not in session:
        return redirect('/login')
    username = session['username']
    # get list of all active trades for this user
    now = market_methods.get_market_time()
    queued_list = getGroupedTransactionList(username, max_qty_executed = 0)
    grouped_list = getGroupedTransactionList(username, min_qty_executed=1)
    recent_complete_list = getGroupedTransactionList(username, completed=True, start_date=now - MAX_AGE, end_date=now)

    return render_template('active-list.html', queued_transactions=queued_list[::-1], transactions=grouped_list[::-1], complete_transactions=recent_complete_list[::-1])

@app.route('/history', methods=['GET', 'POST'])
def show_history():
    if 'username' not in session:
        return redirect('/login')
    username = session['username']
    if request.method == 'POST':
        if request.form['start_date'] == '' or request.form['end_date'] == '':
            context = dict(error_message = "No quantity given")
            recent_complete_list = getGroupedTransactionList(username, completed=True, date_format='%m/%d/%Y')
            return render_template("completed-list.html", complete_transactions=recent_complete_list[::-1], **context)
        temp_start_date = str(request.form['start_date'])
        temp_end_date = str(request.form['end_date'])
        try:
            t = datetime.datetime.strptime(temp_start_date, "%m/%d/%Y")
            start_date = time.mktime(t.timetuple())
            t = datetime.datetime.strptime(temp_end_date, "%m/%d/%Y")
            end_date = time.mktime(t.timetuple())
        except:
            context = dict(error_message="Invalid date range: format incorrect")
            recent_complete_list = getGroupedTransactionList(username, completed=True, date_format='%m/%d/%Y')
            return render_template('completed-list.html', complete_transactions=recent_complete_list[::-1], **context)
        if (not validity_checker.valid_history_date_range(start_date, end_date)):
            context = dict(error_message = "Invalid date range")
            recent_complete_list = getGroupedTransactionList(username, completed=True, date_format='%m/%d/%Y')
            return render_template('completed-list.html', complete_transactions=recent_complete_list[::-1], **context)

        recent_complete_list = getGroupedTransactionList(username, completed=True, start_date=start_date, end_date=end_date, date_format="%m/%d/%Y")
    else:
        recent_complete_list = getGroupedTransactionList(username, completed=True, date_format='%m/%d/%Y')
    return render_template('completed-list.html', complete_transactions=recent_complete_list[::-1])

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
        if (not validity_checker.valid_username(username)):
            context = dict(error_message = "Invalid username")
            return render_template("create.html", **context)
        
        if (not validity_checker.valid_password(request.form['password'])):
            context = dict(error_message = "Invalid password")
            return render_template("create.html", **context)

        # get the user object from the database
        user = getUser(username)
        if user != None:
            context = dict(error_message = "User name already exists")
            return render_template("create.html", **context)
        # insert new user record into the database
        insertNewUser(username, passhash)
        if 'username' in session:
            return redirect('/logout')
        return redirect('/')
    return render_template("create.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if 'username' in session:
            return redirect('/logout')
        if request.form['username'] == '' or 'username' not in request.form:
            context = dict(error_message = "No username given")
            return render_template("login.html", **context)
        username = request.form['username']
        if request.form['password'] == '' or 'password' not in request.form:
            context = dict(error_message = "No password given")
            return render_template("login.html", **context)
        user = getUser(username)
        if user == None:
            return render_template('login.html', error="Incorrect username or password")
        passhash = user.password
        if passhash == None:
            return render_template('login.html', error="Incorrect username or password")
        password = request.form['password']
        if passhash != hashlib.md5(password).hexdigest():
            return render_template('login.html', error="Incorrect username or password")
        session['username'] = request.form['username']
        return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

def process_command_line_args(argv):
    num_args = len(argv) 
    if (num_args == 1):
        return
    if (argv[1] == 'print_prices'):
        max = 0
        min = -1
        counter = 0
        try:
            while (True):
                quote = market_methods.get_market_quote()
                timestamp = quote['timestamp']
                price = quote['top_bid']['price']
                if (price == -1):
                    continue
                if (min == -1):
                    min = price
                if (price < min):
                    min = price
                if (price > max):
                    max = price
                print timestamp
                print price
                counter = counter + 1
        except TypeError:
            print "done"
    else:
        print 'unknow arg'
    print "max %d" % max
    print "min %d" % min

if __name__ == '__main__':
    process_command_line_args(sys.argv)
    DATABASE_URI = "postgresql://localhost/master_4156_database"
    database_methods.engine = create_engine(DATABASE_URI)
    database_methods.Session = sessionmaker(bind=database_methods.engine)
    createSchema()
    my_queue = Queue(maxsize=0)
    num_threads = multiprocessing.cpu_count()
    for i in range(num_threads):
        worker = Thread(target=process_workload, args=(my_queue,))
        worker.setDaemon(True)
        worker.start()
    app.run()
