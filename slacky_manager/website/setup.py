from aiohttp import web
from website import handles as h
import aiohttp_jinja2
import jinja2


def get_webapp():
    app = web.Application()
    aiohttp_jinja2.setup(app,
        loader=jinja2.FileSystemLoader('./website/templates'))
    routes = [web.get('/', h.report)]
    app.add_routes(routes)
    return web.AppRunner(app)
