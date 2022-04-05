from slack_bolt.app.async_app import AsyncApp
from os import environ

app = AsyncApp(token=environ["SLACK_BOT_TOKEN"])
