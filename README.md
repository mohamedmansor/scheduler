# About

The main objective of webtask_scheduler project is to be  a service that allows us to execute scheduled tasks.
For simplicity, let’s assume that tasks can be triggered by accessing a web URL. You create
a task by providing a URL and the desired time to run.
When the specified time arrives, the service will call the URL.

# 🏛️ The Solution decisions


I've reused the `PeriodicTask` Model to make use of it's features to create a model instance that will store task info.
If I was about to build my Own model for our case in the project context, I would cloned some of it's fields (name, task, clocked).
I found it fit our need in this project But in a bigger context we might need to add UUID field.

The usage of User app is to enable login and creating a superuser account with email as an identifier instead of username. So that reviewer can view the tasks list and filter though them.


I've Created the `compose` directory with `local` sub-directory, and inside it contains the start shell scripts for used services (flower, beat, and worker) in addition to `Dockerfile` The reason for this decision was to make it easy to deploy the app on different environment. All is needed is to create another directory with same directory structure and use it in the related compose file.

# Scheduler APIs

`/timer` Receives a JSON object containing hours, minutes, seconds, and a web url.

Return task ID and time left in seconds.

**The good bractice for such a service is to create a model that inherits from `PeriodicTask` and Add replace the `pk` with `UUID`. This was skiped to avoid extra complexity and make project easy for review.**

`/timer/{timer_uuid}` Receives the timer id in the URL, as the resource uuid. 

Returns a JSON object with the amount of seconds left until the timer expires.
If the timer already expired, returns 0.


# 💻 Running Locally

1. Go to `webtask_scheduler` directory

```bash
cd webtask_scheduler
```

2. Build

```bash
docker compose -f docker-compose.local.yml build
```

3. Run

```bash
docker compose -f docker-compose.local.yml up
```

4. Access Swagger Docs using the below url

```
0.0.0.0:8000/api/docs
```

# 🔨 Usage
For the ease of use the Authentication and Authorization was skiped.
Assuming it's a public APIs to create/retrive tasks. But it depends on the app usage Authentication and Authorization can be added accordingly.

### Set timer

Use swagger docs url `0.0.0.0:8000/api/docs/#/scheduler/v1_scheduler_timer_create` to test setting timer by providing hours, minutes, seconds and web_url values.

Validation Fields (hours, minutes, seconds) must be integer and greater than or equal zero.

### Get timer

Use swagger docs url `0.0.0.0:8000/api/docs/#/scheduler/v1_scheduler_timer_retrieve` to test getting a timer with provided task ID or return 404 status code if ID was not found.

### List all Tasks

This step requires a **superuser account**.
> PS: default login/register identifier is email instead of username

1. Create admin user

```bash
docker-compose -f docker-compose.local.yml exec django /entrypoint python manage.py createsuperuser
```

2. Enter email and password

3. Open `0.0.0.0:8000/admin/django_celery_beat/periodictask`

# 🧪 Tests

Running the all project tests at once using `pytest` Use this command

```bash
docker-compose -f docker-compose.local.yml exec django /entrypoint pytest
```

In case of running single function Use this command

```bash
docker-compose -f docker-compose.local.yml exec django /entrypoint pytest -s -vv -k <test_function>
```

# 🚀 Production mode

To avoid adding more complexity to the project Some of the production configurations was skiped. However in order to deploy and run this application into production environment you should:

### Translation

- by creating `webtask_scheduler/locale/<language>`
- configuring the `LANGUAGES` settings in `base.py`, by uncommenting languages you are willing to support. Then, translations strings will be placed in this folder when running
- Make messages `docker-compose -f docker-compose.local.yml exec django /entrypoint python manage.py makemessages --no-location`
- Once all translations are done, they need to be compiled into `.mo` files (stands for Machine Object), which are the actual binary files used by the application `docker compose -f docker-compose.local.yml run --rm django python manage.py compilemessages`

> The production image runs `compilemessages` automatically at build time, so as long as your translated source files (PO) are up-to-date, you're good to go.


### Add monitoring tools

- Sentry Using`sentry-sdk` Add `SENTRY_DSN` to `.envs/.production/.django` (Use gitcrypt to encrypt production envs)
- Add Datadog for logs

### Create a docker-compose.production.yml

- Add production services with production envs
- Add Dockerfile for Django and Postgres
- Add start and entrypoint bash script in each one according to the project need
- Finally build the project then Push image to ECR or run it using compose up command.

### Default error pages

Finally Add to templates directory the default error page 400, 403, 500 html files. Then Update `config/urls.py` with Error path and template.
