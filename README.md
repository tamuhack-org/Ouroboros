[![codecov](https://codecov.io/gh/tamuhack-org/Ouroboros/branch/main/graph/badge.svg)](https://codecov.io/gh/tamuhack-org/Ouroboros)

# :snake: Hiss

An open-source, hackathon registration system. :school:


## :computer: Running Locally

### Local development

The fastest way to develop locally is with [uv](https://docs.astral.sh/uv/).

```sh
uv venv --python 3.12
uv sync

source .venv/bin/activate
python ./hiss/manage.py migrate #Apply all migrations

python ./hiss/manage.py createsuperuser


python ./hiss/manage.py runserver
```

### Mimic Production

To mimic production, we highly encourage using [Docker Compose](https://docs.docker.com/compose/).

After Docker Compose is installed, there are just a few steps left for first-time setup:

```shell script
docker-compose up -d
docker-compose exec db su postgres # Currently on host, moving into container
psql # Currently in container, moving into PostgreSQL prompt 
```
Now that you're in the PostgreSQL prompt, just run

```sql
CREATE DATABASE hiss;
```

This will create the database for you, and you're done with setup!

```shell script
exit # In the PostgreSQL prompt, moving to container
exit # In the container, moving to the host
```

Now that you're on the host machine, just run the following:

```shell script
docker-compose run web python3 manage.py makemigrations # Only if you modified models.py or forms.py
docker-compose run web python3 manage.py migrate --run-syncdb
docker-compose exec web python3 manage.py loaddata application/fixtures/schools.json # Loads in schools for school dropdown in application
docker-compose run web python3 manage.py createsuperuser # Enter details for an admin user to access the admin panel.
```

You're all set! Just run `docker-compose up` and you're good to go!


To use it, simply replace the values in `docker-compose.prod.yml` with the values you need, and run

```shell script
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```


# CRON job configuration
This project includes a cron job to automatically expire unconfirmed applications.

The Django management command is located at:
application/management/commands/expire.py

To run it manually:

```sh
python manage.py expire
```

On Railway, this is scheduled via a cron job (e.g., daily at 11:59 PM CST) to:

Mark unconfirmed applications as expired

Send notification emails to affected users

Ensure your environment variables (e.g., SECRET_KEY, DATABASE_URL, email settings) are set correctly when running this command.

## Contributing
We now use uv for dependency management, ensure that uv is installed.

```sh
uv venv --python 3.12
uv sync

source .venv/bin/activate
python ./hiss/manage.py migrate #Apply all migrations

python ./hiss/manage.py createsuperuser


python ./hiss/manage.py runserver
```

```
/admin/csv-emails/judges/
/admin/csv-emails/mentors/
```

# Brought to you by

![TAMUhack](/resources/img/TAMUhack.png)
