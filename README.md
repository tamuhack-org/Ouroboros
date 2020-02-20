![TAMUhack](https://raw.githubusercontent.com/samarthdave/Ouroboros/master/resources/img/TAMUhack.png)
# :snake: Hiss

An open-source, hackathon registration system. :school:

## :question: Questions

If you have questions, we might've answered them already on the [wiki](https://github.com/tamuhack-org/Ouroboros/wiki)! Check it out.

## :computer: Running Locally

For local development, this application is self-contained (it uses a SQLite table). Just follow the steps below!

1. Create a virtualenv for Python 3.6 (`python3 -m venv env`)
2. `source env/bin/activate`
3. `cd hiss`
4. `pip install -r requirements.txt`
5. `python3 manage.py makemigrations application customauth user`
6. `python3 manage.py migrate --run-syncdb`
7. `python3 manage.py loaddata application/fixtures/*.json`
8. `python3 manage.py seeddb <NUM_USERS_WHO_CREATED_AN_ACCOUNT> <NUM_USERS_WHO_APPLIED> <NUM_USERS_WE'VE_ALREADY_ACCEPTED>`
9. `python3 manage.py createsuperuser`
10. `python3 manage.py runserver`
