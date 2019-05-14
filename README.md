# Ouroboros

A modular, open-source, fully-customizable hackathon management system.

## Setting Up

There's two ways of running Ouroboros: by using Docker, or by installing the dependencies yourself.

In either case, there are really _X_ steps involved in getting the app running:

1. Getting PostgreSQL (Taken care of by Docker)
2. Installing dependencies for the app (Taken care of by Docker)
3. Making Django migrations (must be performed manually)
4. Creating the SQL database and tables
5. Creating the superuser
6. Running the server

### Docker

This guide assumes you have [Docker](https://docs.docker.com/install/) and [Docker-Compose](https://docs.docker.com/compose/install/) installed.

For convenience, we've included a `docker-compose.yml` file in our repository.

To start the containers, simply enter into your command prompt (not sure how this works on Windows):

```sh
docker-compose up --build
```

This will start all of the required containers, and get the server running. In a separate terminal, you'll need to run the following two commands:

```sh
docker exec -it ouroboros python3 manage.py makemigrations hacker --settings=ouroboros.settings.docker_dev
docker exec -it ouroboros python3 manage.py migrate --settings=ouroboros.settings.docker_dev
```

From there, you should be able to go through most of the website.

In order to go through the entire registration progress, however, you'll need to create an admin user. You can do this by doing:

```sh
docker exec -it ouroboros python3 manage.py createsuperuser --settings=ouroboros.settings.docker_dev
```

You should only need to run the above command once.

Follow the prompts provided, and you should be able to approve users' applications, and go through the rest of the site.

## Running on Host

The other way of running the app is to run it on your local machine. This involves installing [PostgreSQL](https://www.postgresql.org/download/). In these instructions, it's assumed that Postgres is installed and running, and a database named `ouroboros` has been created.

1. Create a virtualenv for Python 3.6 (`python3 -m venv env`)
2. `pip install -r requirements.txt`
3. `python3 manage.py makemigrations hacker`
4. `python3 manage.py migrate --run-syncdb`
5. `python3 manage.py createsuperuser`
6. `python3 manage.py runserver`
