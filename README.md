# healthy-meals: Meet your Dietary Goals with Healthier Meals

[![CircleCI](https://dl.circleci.com/status-badge/img/circleci/BZR3uzdbU6P9JdMbhCLMmZ/PhQcorR5decQrvhgn17chH/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/circleci/BZR3uzdbU6P9JdMbhCLMmZ/PhQcorR5decQrvhgn17chH/tree/main)
[![Python Code Coverage Status](https://tayloredwebsites.github.io/healthy-meals/coverage_py/coverage_badge.svg)](https://tayloredwebsites.github.io/healthy-meals/coverage_py/html/index.html)
[![All Coverage Status](https://tayloredwebsites.github.io/healthy-meals/coverage/coverage_badge.svg)](https://tayloredwebsites.github.io/healthy-meals/coverage/html/index.html)
[![Test Status](https://tayloredwebsites.github.io/healthy-meals/tests/tests_badge.svg)](https://tayloredwebsites.github.io/healthy-meals/tests/index.html)
[![](https://tayloredwebsites.github.io/healthy-meals/flake8/flake8_badge.svg)](https://tayloredwebsites.github.io/healthy-meals/flake8/html/index.html)
[![](https://tayloredwebsites.github.io/healthy-meals/mypy/mypy_badge.svg)](https://tayloredwebsites.github.io/healthy-meals/mypy/index.html)

[Documentation](https://tayloredwebsites.github.io/healthy-meals/index.html)

## Table of Contents
* [Project Features](#project-features)
* [Next Steps for Project](#next-steps-for-project)
* [Installation](#installation)
* [Development Environment Guide](#development-environment-guide)
* [Contributing](#contributing)
* [License](#license)

## Project Features

[TOC](#table-of-contents)

### Keeping a Branch for Starter Base Projects

#### Features for basic website kept in the "BaseStarter" branch
- Runs in Docker or locally (using a local web server).
- Uses the nox tool for automating  and simplifying tasks.
- Automated testing with 100% coverage of all python code.
  - Testing using either testcase and pytest.
  - efficient HTML coverage testing using beautiful soup.
- Uses github actions to ensure all tests pass for pull requests.
  - Test and coverage badges displayed in documentation and in README.md
- Github pages site for Documentation from Sphinx, Test Passing, & Coverage reports
  - Sphinx generated documentation generated in github action and deployed to github pages
  - Automated Testing documentation generated in github action and deployed to github pages
- Django 5.1 & Python 3.12
- Installation via [uv](https://github.com/astral-sh/uv), or [Docker](https://www.docker.com/)
- Sign in by email and password code using [allauth](https://docs.allauth.org/en/latest/)
  - see: [Lithium starter project](https://github.com/wsvincent/lithium)
  - User authentication--log in, sign up, password reset--via [django-allauth](https://github.com/pennersr/django-allauth)
- Static files configured with [Whitenoise](http://whitenoise.evans.io/en/stable/index.html)
- Styling with [Bootstrap v5](https://getbootstrap.com/)
- Debugging with [django-debug-toolbar](https://github.com/jazzband/django-debug-toolbar)
- DRY forms with [django-crispy-forms](https://github.com/django-crispy-forms/django-crispy-forms)
- Custom 404, 500, and 403 error pages
- Internationalization (i18n) of strings in code
- Soft Delete functionality of database records
- Base HTML Template
  - sub-template blocks for pages and partial pages
  - SCSS translation to CSS using Dart SASS
    - [libsass is deprecated, dart sass is recommended](https://sass-lang.com/blog/libsass-is-deprecated/)
    - [https://sass-lang.com/dart-sass/](https://sass-lang.com/documentation/cli/dart-sass/)
  - site wide font sizing tool
  - login with email/password using [allauth](https://docs.allauth.org/en/latest/)
  - signup

### Starter Base Project Todo List

[To Do List in Documentation](https://tayloredwebsites.github.io/healthy-meals/todos.html)

## Next Steps for Project

[TOC](#table-of-contents)

### Completed Main Project Features

Sorry, we are just starting this.

### Main Project Features Next Steps

#### 0) Good ways to get started with this project:

- Documentation Updates
  - make a pull request with documentation updates
  - document the process to make documentation update pull requests
- Feature Requests
  - Please feel free to make feature requests
    - note we are very early in project development
- Development and Documentation standards enhancements
  - suggestions for standards are best done earlier in project development
  - getting QA tools working, such as MyPy or Ruff will be greatly apprecieated.
- see: [todo items, especially the If you are looking for an issue to work on... todo list](https://tayloredwebsites.github.io/healthy-meals/todos.html#current-to-do-items-listings)


#### Major Step 1) Wiki (with built in references tooling)

- include django_wiki project to deliver main UI to site

- references table will be integrated with the wiki to provide references to information on wiki, as well as who put in the information.

#### Major Step 2) Consumables Table

- This table will be designed so that all variety of consumables such as food, supplements, herbs, medicines will be in this system.

#### Major Step 3) Consumable Aspects Table

- This table will be used to keep track of the important dietary aspects of consumables.  This will include:
  - Vitamins
  - Minerals
  - Nutrients
  - Anti-nutrients (such as oxalates).
  - Additives
  - Preservatives
- The amounts from the aspect's sample analysis will be stored such that an average value and variance of the aspect will be available for display

#### Major Step 4) and so much more...


## Installation

[TOC](#table-of-contents)

To Do: review installation instructions

### 1) fork and clone repo(sitory) from github

see: [Fork a Github Repo](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo)

see: [Clone a Github Repo](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)

### uv
You can use [uv](https://docs.astral.sh/uv/) to create a dedicated virtual environment.

```
$ uv sync
```

Then run `migrate` to configure the initial database. The command `createsuperuser` will create a new superuser account for accessing the admin. Execute the `runserver` command to start up the local server.

```
$ uv run manage.py migrate
$ uv run manage.py createsuperuser
$ uv run manage.py runserver
# Load the site @ http://127.0.0.1:8000
# Load the Django Admin pages @ http://127.0.0.1:8000/admin
```

### Pip
To use Pip, create a new virtual environment and then install all packages hosted in `requirements.txt`. Run `migrate` to configure the initial database. and `createsuperuser` to create a new superuser account for accessing the admin. Execute the `runserver` command to start up the local server.

    * Note: <code folder> is your projects parent directory
    $ cd <code folder>
    $ git clone git@github.com:<yourGithubUsername>/healthy-meals.git
    $ cd healthy-meals
    $ git remote add upstream git@github.com:tayloredwebsites/healthy-meals.git

###  2) ASDF Installation (To Do: review this)

See: [ASDF install](https://asdf-vm.com/guide/getting-started.html), and [ASDF configuration](https://asdf-vm.com/manage/configuration.html)

    $ cat .tool-versions
      * you should see (with possible version differences):
      *    python 3.12.6
      *    direnv 2.34.0

### 3) installation of venv and direnv (working with asdf) (To Do: review this)

see: # [https://mdaverde.com/posts/python-venv-direnv-asdf/](https://mdaverde.com/posts/python-venv-direnv-asdf/)


    * Note: <code folder> is your projects parent directory
    $ cd <code folder>/healthy-meals  # see clone repo from github
    $ python -m venv .venv
    $ echo "export VIRTUAL_ENV=$PWD/.venv\nexport PATH=$PWD/.venv/bin:\$PATH\nexport PYTHONPATH=$PWD" > .envrc
      * You should get: "direnv: error <code folder>/healthy-meals/.envrc is blocked. Run `direnv allow` to approve its content"
    $ direnv allow
    $ which python
      * you should see python3 running from the .venv directory
      *   <code folder>/healthy-meals/.venv/bin/python3
    $ cd ..
    $ cd healthy-meals
      * you will see the following messages entering your directory
      *   direnv: loading .../.envrc
      *   direnv: export +PYTHONPATH +VIRTUAL_ENV ~PATH
    $ cat .envrc
      * You should see the following listing for your .envrc file
      * export VIRTUAL_ENV=<code folder>/healthy-meals/.venv
      * export PATH=<code folder>/healthy-meals/.venv/bin:$PATH
      * export PYTHONPATH=<code folder>/healthy-meals/.venv/bin


### 4) install required software into .venv


Note: We use [nox](https://nox.thea.codes/en/stable/index.html) for automation of tasks

Instructions:

    $ nox -s setupEnv

### 5) install postgres locally

Note: you may skip this step if you will be only using docker.

for brew install on mac: [https://daily-dev-tips.com/posts/installing-postgresql-on-a-mac-with-homebrew/](https://daily-dev-tips.com/posts/installing-postgresql-on-a-mac-with-homebrew/)

for other installs: [https://www.enterprisedb.com/docs/supported-open-source/postgresql/installing/](https://www.enterprisedb.com/docs/supported-open-source/postgresql/installing/)


Note: If you are having problems with installing postgres onto your computer, consider using docker desktop


### 6) install docker desktop

Note: You may skip this step if you are only developing locally, or have the Docker Daemon or Desktop installed already.

### 7) install dart sass

Note: the libsass used by many python programs has been deprecated and dart-sass is now recommended

See: [https://sass-lang.com/blog/libsass-is-deprecated/](https://sass-lang.com/blog/libsass-is-deprecated/)

see: [https://github.com/sass/dart-sass](https://github.com/sass/dart-sass)

See: [https://sass-lang.com/install/](https://sass-lang.com/install/)

#### Mac

    % brew install sass/sass/sass
    % sass --version

#### Linux (using Snap)

See: [https://snapcraft.io/dart-sass](https://snapcraft.io/dart-sass)

    $ sudo snap install dart-sass
    % sass --version

#### docker

Note: Our Dockerfile downloads dart-sass and adds it to the path

## Development Environment Guide

[TOC](#table-of-contents)

### Docker Development

### Local Development

## Contributing

[TOC](#table-of-contents)

Please enter issues or pull requests (initially) for the following:
- Documentation issues, updates, or feature requests
- Base Starter branch issues, updates, or feature requests
- Application feature requests

If you have any questions, or are interested in contributing to the software development, please email [David Andrews Taylor of Taylored Web Sites](mailto:tayloredwebsites@me.com)

## License

[TOC](#table-of-contents)

Copyright (C) 2025 David A. Taylor of Taylored Web Sites (tayloredwebsites.com)
Licensed under [AGPL-3.0-only](https://opensource.org/license/agpl-v3/), and let me know how you wish to help.

[Why AGPL V3?](https://www.fsf.org/bulletin/2021/fall/the-fundamentals-of-the-agplv3)