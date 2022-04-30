from aiohttp_jinja2 import template
from dboper import get_lab_table


@template('report.html')
async def report(req):
    return await get_lab_table()
