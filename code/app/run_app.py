import subprocess 
import socket
import time

def run_app():
    while (True):
        try:
            print "About to run python server.py"
            subprocess.call(["python", "server.py"])
            print "app crashed - about to restart after sleeping"
            time.sleep(5)
        except socket.error, e:
            print str(e)
            print "App received error - trying again"
            continue

run_app()
