# Instructions and Notes

### Create a virtual env:
```
virtualenv venv
```

### Activate the virtual env:
```
. venv/bin/activate
```

### Install requirements:
```
pip install -r requirements.txt
```

### Setting up database:
```
Drop table userpass if old schema, then simply run python server.py - it creates new schema
```
###To run server:
```
1) Need exchange server to be running -> python server.py from exchange_simulator/ dir
2) Make sure a virtual envionrment has been activated (run '. venv/bin/activate/ from dir where venv dir is)
3) Make sure postgres is running
3) Go to code/app/ dir and run: python server.py
```

###Testing Instructions
```
To run all tests in tests/ dir: 
1) cd code/
2) python -m unittest discover tests

To run one specific test file from tests/ dir (e.g. test__order.py):
1) cd code/
2) python -m unittest tests.test_order

To calculate test coverage:
1) cd code/
2) coverage run --source=app/  -m unittest discover tests
3) coverage report -m
```
