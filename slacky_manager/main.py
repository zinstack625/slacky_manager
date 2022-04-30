#!/usr/bin/env python3

from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from os import environ
import slack_app
if "START_WEB" in environ:
    import website
    from aiohttp import web
from dboper import init_db

import mentor
import mentor_manage
import submitter


async def main():
    handler = AsyncSocketModeHandler(slack_app.app, environ['SLACK_APP_TOKEN'])
    await init_db()
    if "START_WEB" in environ:
        webrunner = website.setup.get_webapp()
        await webrunner.setup()
        resource = web.TCPSite(webrunner, '0.0.0.0', '8080')
        asyncio.create_task(resource.start())
    await handler.start_async()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
