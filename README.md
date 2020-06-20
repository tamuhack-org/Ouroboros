![TAMUhack](/resources/img/TAMUhack.png)
# :snake: Hiss

An open-source, hackathon registration system. :school:

## :question: Questions

If you have questions, we might've answered them already on the [wiki](https://github.com/tamuhack-org/Ouroboros/wiki)! Check it out.

## :computer: Running Locally

### Local Development

For local development, we highly encourage using [Docker Compose](https://docs.docker.com/compose/).

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
docker-compose exec web python3 manage.py loaddata application/fixtures/schools.json
docker-compose run web python3 manage.py createsuperuser # Enter details for an admin user to access the admin panel.
```

You're all set! Just run `docker-compose up` and you're good to go!

### Mimic Production

To mimic a real production environment, a `docker-compose.prod.yml` file has been included in the repository for you to use.

This file is set up on the assumption that you are using [Mailgun](https://mailgun.com) as your team's email provider.

To use it, simply replace the values in `docker-compose.prod.yml` with the values you need, and run

```shell script
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```