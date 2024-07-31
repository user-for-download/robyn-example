# Robyn-example-auth-stratz-dota2

- use https://github.com/sparckles/Robyn
- use https://github.com/wnesbv/robyn-example
- use https://stratz.com/
- use https://www.opendota.com/

# Robyn Example
This repository contains an example project using Robyn, a lightweight web framework for Python.

# Introduction
Robyn Example is a sample project designed to demonstrate the capabilities of the Robyn web framework. 
It provides a basic setup to help you get started with building web applications using Robyn.

# Installation
To get started with this project, follow these steps:

### Clone the repository:
```sh
git clone https://github.com/user-for-download/robyn-example.git
cd robyn-example
```

### Create a virtual environment (optional but recommended):
```sh
python -m venv venv
source venv/bin/activate 
```
### Install the required packages:
```sh
pip install -r requirements.txt
```
### Run
#### Initial migration
use alembic or uncomment
```py
#await on_app_startup() in main.py
```
```sh
cp .example .env
robyn main.py --dev
```
#### log
```log
INFO:robyn.logger:Starting server at http://0.0.0.0:8081
```