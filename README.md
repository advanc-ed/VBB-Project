# VBB Telegram Bot

### Bot for finding journey information via VBB API

![Telegram](https://img.shields.io/badge/Telegram-blue?style=flat&logo=telegram)
![PythonVersions](https://img.shields.io/pypi/pyversions/aiogram)
![aiogram 3](https://img.shields.io/badge/dev--3.x-aiogram-blue)
![aiogram-dialog](https://img.shields.io/badge/beta--2.x-aiogram__dialog-green)

## Description

The VBB Telegram Bot is a tool that allows users to retrieve journey information for their everyday trips. If a trip is
cancelled, users will receive a notification about it.

## Features

* Stores addresses and user preferences in a Postgresql Database.
* Provides Docker virtualization for both the app and the database.
* Includes a background service that sends users journey updates every morning.
* Offers a good UI, thanks to aiogram-dialog.

## Usage

* 🔑 Add configuration data in `config.toml`

### manual install

* 📎 Install all dependencies from `requirements.txt`

```bash
python -m venv .venv
./.venv/Scripts/activate.ps1 # if you have Windows
source bin/activate          # linux/mac
pip install -r requirements.txt
```

* 🚀 Run the bot using `python -m app`

### docker

```bash
docker-compose up --build
```

## TODO:

* Create an independent VBB package for usage in external apps.
* Enhance usability and optimize code.
* Remove redundant and junk code.