[![CI](https://github.com/tamuhack-org/Ouroboros/actions/workflows/test.yml/badge.svg)](https://github.com/tamuhack-org/Ouroboros/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/tamuhack-org/Ouroboros/branch/main/graph/badge.svg)](https://codecov.io/gh/tamuhack-org/Ouroboros)

# :snake: Hiss

An open-source, hackathon registration system. :school:

## Quickstart (local)
```sh
uv venv --python 3.12
uv sync
source .venv/bin/activate
python hiss/manage.py migrate
python hiss/manage.py createsuperuser
python hiss/manage.py runserver
```

## Testing
Uses a dedicated settings file for faster runs.
```sh
cd hiss
python manage.py test --settings=hiss.settings.test --parallel
# or target a subset
python manage.py test application.tests.view_tests.create --settings=hiss.settings.test
```

## Environment configuration
- Copy `.env.dist` to `.env` and fill required values (e.g., `SECRET_KEY`, database credentials, email backend, storage keys).
- For Docker, ensure DB credentials match `docker-compose.yml`; production-like overrides live in `docker-compose.prod.yml`.

## Running with Docker (production-like)
```sh
docker-compose up -d
docker-compose exec db psql -U postgres -c "CREATE DATABASE hiss;"
docker-compose run web python3 manage.py migrate --run-syncdb
docker-compose exec web python3 manage.py loaddata application/fixtures/schools.json
docker-compose run web python3 manage.py createsuperuser
docker-compose up
```
To combine overrides: `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up`.

## Deploying to staging
If using the existing flow, push your feature branch to staging (force push replaces the staging ref—double-check before running):
```sh
git push -f origin origin/feature:staging
```

## Scheduled expiration (cron)
The `expire` management command marks unconfirmed applications as expired and sends notification emails.
```sh
python manage.py expire
```
Location: `hiss/application/management/commands/expire.py`. On Railway, schedule this daily (e.g., 11:59 PM CST) with required env vars present.

## Admin utilities
- `/admin/csv-emails/judges/` – CSV email interface for judges
- `/admin/csv-emails/mentors/` – CSV email interface for mentors

## Contributing
- Install uv and follow the Quickstart steps above.
- Keep tests green and prefer `--parallel` when running locally.

## License
MIT. See `LICENSE`.

## Brought to you by
![TAMUhack](/resources/img/TAMUhack.png)
