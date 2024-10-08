# SWD Django Demo
The project can be used as a reference for the SWD lab course.
This project consists of several apps with a focus on loose coupling and dependency injection.
A good article about separation of concerns in Django projects can be found `https://emcarrio.medium.com/business-logic-in-a-django-project-a25abc64718c`.
Good Django tutorials can be found `https://www.djangoproject.com/start/` or `https://cs50.harvard.edu/web/2020/weeks/3/`.

## Requirements
You need to have a working python installation on your local system. Best-Practise is to use python from the official website: https://www.python.org/.
Please use the **latest 3.11** version available (https://www.python.org/downloads/). 

Notice: The version 3.12 seems NOT to be compatible with the dependency-injector-package (https://python-dependency-injector.ets-labs.org/main/changelog.html)


## Installation

1. Clone the repository. `git clone git@its-git.fh-salzburg.ac.at:SWD/djangodemo.git` or `git clone https://its-git.fh-salzburg.ac.at/SWD/djangodemo.git`
2. Install Poetry: `https://python-poetry.org/docs/#installation`
   - Mac/Linux: `curl -sSL https://install.python-poetry.org | python3 -`
   - Windows (Powershell): `(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -`
     - Note: On Windows sometimes `python` does not work in the shell but the alias `py` does!
     - Note: When you want to exectue python in a shell and the Windows App-Store opens - you need to deactive this Windows-Behavior: https://stackoverflow.com/questions/58754860/cmd-opens-windows-store-when-i-type-python
     - Note: On Windows you have to add poetry to the path: `%APPDATA%\Python\Scripts`

### Usage

1. Activate the virtual environment: `poetry shell`.
2. Install dependencies with the projects main directory: `poetry install`.
3. Create the database tables: `python manage.py migrate`
4. Create an admin user: `python manage.py createsuperuser`
5. Run unit tests: `python manage.py test -v 2`
6. Run the development server: `python manage.py runserver`.
7. Open the website in your browser: `http://localhost:8000/admin`, `http://localhost:8000/products`.

## IDE
There are a number of IDEs available for python development. You can choose between different variants like [VSCode](https://code.visualstudio.com/), [PyCharm](https://www.jetbrains.com/pycharm/), [VIM](https://realpython.com/vim-and-python-a-match-made-in-heaven/), ...

## Dependency Injection
This project uses the python dependency injection module, which is not part of Django itself.
`https://python-dependency-injector.ets-labs.org/examples/django.html`



