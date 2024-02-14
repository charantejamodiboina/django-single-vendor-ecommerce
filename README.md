# Create Virtual enironment
create venv using following command.

for windows:

`python -m venv venv`

for linux:

`python3 -m venv venv`

#  Activate venv by using this command
for windows:

`venv\Scripts\activate.bat`

for linux:

`source venv/bin/activate`

# Installation
Make sure Python is installed.

Install requirements using following command.

`pip install -r requirements.txt`

# Now make the migrations.
for windows:

`python manage.py makemigrations`

for linux:

`python3 manage.py makemigrations`

# Migrate the models to your db.
for windows:

`python manage.py migrate`

for linux:

`python3 manage.py migrate`

# Run server using this command
for windows:

`python manage.py runserver`

for linux:

`python3 manage.py runserver`

# Run the app.

Open the app at `localhost:8000` or `http://127.0.0.1:8000/`
