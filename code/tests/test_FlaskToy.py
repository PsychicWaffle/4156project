import os
import tempfile
import pytest
import random
from FlaskToy import FlaskToy

@pytest.fixture
def client(request):
    db_fd, FlaskToy.app.config['DATABASE'] = tempfile.mkstemp()
    FlaskToy.app.config['TESTING'] = True
    client = FlaskToy.app.test_client()

    return client

def create_user(client):
    username = str(random.randint(10000,5000000))
    password = str(random.randint(10000,5000000))
    return client.post('/create', data=dict(
        username = username,
        password = password,
        password_conf = password
    )), username, password



def login(client,username,password):
    return client.post('/login', data=dict(
        username=username,
        password=password,
    ), follow_redirects=True)

client = client('/')

def test_create():
    rv, username, password = create_user(client)
    rv = login(client, username, password)
    assert 'Hello, %s!' % username in rv.data

def test_login():
    rv = login(client,'hello','hello')
    assert 'Hello, hello!' in rv.data


test_login()
test_create()

print("All tests passed!")