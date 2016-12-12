import subprocess 
import socket

def run_app():
    while (True):
        process = None
        try:
            subprocess.call(["python", "server.py"])
        except socket.error, e:
            print str(e)
            print "App received error - trying again"
            continue

run_app()
