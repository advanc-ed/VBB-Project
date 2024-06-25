import argparse

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import sessionmaker

from .config import Config, parse_config


def parse_arguments():
    parser = argparse.ArgumentParser(description="Process app configuration.")
    parser.add_argument(
        "--test", "-t", help="test bot token", action="store_true")
    return parser.parse_args()


owner_id: int
dp: Dispatcher
sessionmanager: sessionmaker
bot: Bot
config: Config = parse_config("config.toml")
arguments = parse_arguments()
scheduler = AsyncIOScheduler()
