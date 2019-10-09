# Hiss

An open-source, hackathon registration system.

## Questions

If you have questions, we might've answered them already on the wiki! Check it out.

## Running Locally

For local development, this application is self-contained (it uses a SQLite table). Just follow the steps below!

1. Create a virtualenv for Python 3.6 (`python3 -m venv env`)
2. `cd hiss`
3. `pip install -r requirements.txt`
4. `python3 manage.py makemigrations application customauth rsvp user`
5. `python3 manage.py migrate --run-syncdb`
6. `python3 manage.py createsuperuser`
7. `python3 manage.py runserver`

