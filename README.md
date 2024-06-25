# 🚀 VBB Telegram Bot

### Your Personal Journey Companion via VBB API

![Telegram](https://img.shields.io/badge/Telegram-blue?style=flat&logo=telegram)
![PythonVersions](https://img.shields.io/pypi/pyversions/aiogram)
![aiogram 3](https://img.shields.io/badge/dev--3.x-aiogram-blue)
![aiogram-dialog](https://img.shields.io/badge/beta--2.x-aiogram__dialog-green)

## 🌟 Description

The **VBB Telegram Bot** is your go-to tool for effortless journey planning and updates. Receive real-time information
on your trips and get notified instantly if a journey is cancelled.

## 🔧 Usage Features

- 🕒 **Next Departures**: Quickly find the next departures at nearby stops.
- 🛤️ **Detailed Journey Info**: Access comprehensive journey details to your favorite addresses.
- 🗺️ **Address Management**: Easily manage your address database.

## 💻 Tech Features

- 🗄️ **Async PostgreSQL Database**: Securely stores addresses and user preferences (via SQLAlchemy).
- 🐳 **Docker Virtualization**: Provides containerization for both the app and the database.
- 🕰️ **Background Service**: Sends users journey updates every morning.
- 🎨 **User Interface**: Smooth and intuitive UI powered by aiogram-dialog.

## 🚀 Getting Started

* 📄 Add your configuration details in `config.toml`

### 📦 Manual Installation

1. **Create a new virtual environment**

    ```bash
    python -m venv .venv
    ```

2. **Activate the virtual environment**

    - Windows:
        ```powershell
        ./.venv/Scripts/activate.ps1
        ```
    - Linux/MacOS:
        ```bash
        source .venv/bin/activate 
        ```

3. **Install all dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the bot**

    ```bash
    python -m app
    ```

### 🐳 Docker

1. **Build and start the services**

    ```bash
    docker-compose up --build
    ```

## 📅 Future Plans

- 📦 **Independent VBB Package**: Develop a standalone VBB package for integration into other apps.
- 🛠️ **Usability Enhancements**: Improve user experience and optimize the codebase.
- 🧹 **Code Cleanup**: Remove redundant and unnecessary code (primarily dialogs and message builders).
