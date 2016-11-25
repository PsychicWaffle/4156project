import database_methods
from transaction import *
import multiprocessing

def add_workload_to_queue(q, workload):
        print "processing workload"
        database_methods.updateTransactionQueuedStatus(workload[0], True)
        q.put(workload)

def process_workload(q):
    print "processing workload"
    while True:
        workload = q.get()
        # workload = id, username, order object
        database_methods.updateTransactionQueuedStatus(workload[0], False)
        execute_transaction(q, workload[0], workload[1], workload[2])
        q.task_done()

def execute_transaction(q, new_id, username, order_obj):
    # insert new transaction record and grab generated id
    # spin up new process to execute the transaction over time
    transaction_executer = TransactionExecuter(username, new_id)
    transaction_executer.execute_transaction(order_obj)
    curr_tran = database_methods.getTransactionById(new_id)
    if (curr_tran.finished == False):
        remaining_qty = curr_tran.qty_requested - curr_tran.qty_executed
        workload = [new_id, username, order_obj]
        add_workload_to_queue(q, workload)        


