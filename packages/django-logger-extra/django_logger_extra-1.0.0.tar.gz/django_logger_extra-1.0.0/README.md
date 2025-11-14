<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Logger extras for simplified structured logging.](#logger-extras-for-simplified-structured-logging)
  - [Adding django-logger-extra your Django project](#adding-django-logger-extra-your-django-project)
    - [Adding django-resilient-logger Django apps](#adding-django-resilient-logger-django-apps)
    - [Configuring logger formatter in settings.py:](#configuring-logger-formatter-in-settingspy)
    - [Configuring middleware in settings.py:](#configuring-middleware-in-settingspy)
  - [django-auditlog extra context.](#django-auditlog-extra-context)
  - [Logger context usage](#logger-context-usage)
- [Development](#development)
  - [Running tests](#running-tests)
  - [Code format](#code-format)
  - [Git blame ignore refs](#git-blame-ignore-refs)
  - [Commit message format](#commit-message-format)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Logger extras for simplified structured logging.

`django-logger-extra` is a collection of logger extras that makes structured logging setup easier.

## Adding django-logger-extra your Django project

Add `django-logger-extra` in your project's dependencies.

### Adding django-resilient-logger Django apps

To install this logger, add `INSTALLED_APPS` in settings.py:

```python
INSTALLED_APPS = (
    'logger_extra',
    ...
)
```

### Configuring logger formatter in settings.py:
To make use of the JSON formatter it must be configured in setting's LOGGING section.
Filter is optional and brings `logger_context()` contexts available as logger extras.

```python
LOGGING = {
    'filters': {
        'context': {
            '()': 'logger_extra.filter.LoggerContextFilter',
        }
        ...
    },
    'formatters': {
        'json': {
            '()': 'logger_extra.formatter.JSONFormatter',
        }
        ...
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'filters': ['context']
        },
        ...
    },
    ...
}
```

### Configuring middleware in settings.py:
```python
MIDDLEWARE = [
    'logger_extra.middleware.XRequestIdMiddleware',
    ...
]
```

## django-auditlog extra context.
This library can also augment django-auditlog's additional_data fields with active context.
To enable this, optional package `django-auditlog` must be installed and it must be explicitly enabled
in settings.py file.
```python
LOGGER_EXTRA_AUGMENT_DJANGO_AUDITLOG = True
```

## Logger context usage
Active context can be appended with `logger_context` function. It will return current
context as resource. The current context can also be read using function `get_logger_context`.
```python
import logging
from django.http import HttpRequest, JsonResponse

from logger_extra.logger_context import logger_context

logger = logging.getLogger("audit")

def bar():
  with logger_context({ "who": "World" }) as ctx:
    logger.info(f"{ctx['greet']} {ctx['who']}")

def foo():
  with logger_context({ "greet": "Hello" }):
    bar()
    return JsonResponse({})
```

Will result log entry that looks like:
`{"message": "Hello World", "level": "INFO", "time": "2025-04-14T11:08:22.962222+00:00", "context": {"request_id": "95e787b5-4ce8-46ef-bb6e-31651fc8774b", "greet": "Hello", "who": "World"}}`
# Development

Virtual Python environment can be used. For example:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install package requirements:

```bash
pip install -e .
```

Install development requirements:

```bash
pip install -r requirements-test.txt
```

## Running tests

```bash
pytest
```

## Code format

This project uses [Ruff](https://docs.astral.sh/ruff/) for code formatting and quality checking.

Basic `ruff` commands:

* lint: `ruff check`
* apply safe lint fixes: `ruff check --fix`
* check formatting: `ruff format --check`
* format: `ruff format`

[`pre-commit`](https://pre-commit.com/) can be used to install and
run all the formatting tools as git hooks automatically before a
commit.


## Git blame ignore refs

Project includes a `.git-blame-ignore-revs` file for ignoring certain commits from `git blame`.
This can be useful for ignoring e.g. formatting commits, so that it is more clear from `git blame`
where the actual code change came from. Configure your git to use it for this project with the
following command:

```shell
git config blame.ignoreRevsFile .git-blame-ignore-revs
```


## Commit message format

New commit messages must adhere to the [Conventional Commits](https://www.conventionalcommits.org/)
specification, and line length is limited to 72 characters.

When [`pre-commit`](https://pre-commit.com/) is in use, [`commitlint`](https://github.com/conventional-changelog/commitlint)
checks new commit messages for the correct format.
