#!/usr/bin/env python3

from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from os import environ
import slack_app
from dboper import init_db

import mentor
import mentor_manage
import submitter


async def main():
    handler = AsyncSocketModeHandler(slack_app.app, environ["SLACK_APP_TOKEN"])
    await init_db()
    await handler.start_async()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
