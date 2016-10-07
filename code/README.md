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
```sql
CREATE DATABASE USERS;
\connect USERS
CREATE TABLE USERPASS(USERNAME TEXT NOT NULL, PASS TEXT NOT NULL);