# WebTask Scheduler

Behold My Awesome Project!
License: MIT

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest

### Celery

This app comes with Celery.

To run a celery worker:

```bash
cd webtask_scheduler
celery -A config.celery_app worker -l info
```

Please note: For Celery's import magic to work, it is important _where_ the celery commands are run. If you are in the same folder with _manage.py_, you should be right.

To run [periodic tasks](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html), you'll need to start the celery beat scheduler service. You can start it as a standalone process:

```bash
cd webtask_scheduler
celery -A config.celery_app beat
```

or you can embed the beat service inside a worker with the `-B` option (not recommended for production use):

```bash
cd webtask_scheduler
celery -A config.celery_app worker -B -l info
```

### Sentry

Sentry is an error logging aggregator service. You can sign up for a free account at <https://sentry.io/signup/?code=cookiecutter> or download and host it yourself.
The system is set up with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.

# Translations

Start by configuring the `LANGUAGES` settings in `base.py`, by uncommenting languages you are willing to support. Then, translations strings will be placed in this folder when running:

```bash
docker compose -f docker-compose.local.yml run --rm django python manage.py makemessages -all --no-location
```

This should generate `django.po` (stands for Portable Object) files under each locale `<locale name>/LC_MESSAGES/django.po`. Each translatable string in the codebase is collected with its `msgid` and need to be translated as `msgstr`, for example:

```po
msgid "users"
msgstr "utilisateurs"
```

Once all translations are done, they need to be compiled into `.mo` files (stands for Machine Object), which are the actual binary files used by the application:

```bash
docker compose -f docker-compose.local.yml run --rm django python manage.py compilemessages
```

Note that the `.po` files are NOT used by the application directly, so if the `.mo` files are out of dates, the content won't appear as translated even if the `.po` files are up-to-date.

## Production

The production image runs `compilemessages` automatically at build time, so as long as your translated source files (PO) are up-to-date, you're good to go.

## Add a new language

1. Update the [`LANGUAGES` setting](https://docs.djangoproject.com/en/stable/ref/settings/#std-setting-LANGUAGES) to your project's base settings.
2. Create the locale folder for the language next to this file, e.g. `fr_FR` for French. Make sure the case is correct.
3. Run `makemessages` (as instructed above) to generate the PO files for the new language.

# run the project
```bash
docker compose -f docker-compose.local.yml build
```
```bash
docker compose -f docker-compose.local.yml up
```