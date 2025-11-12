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



# Brought to you by

![TAMUhack](/resources/img/TAMUhack.png)
