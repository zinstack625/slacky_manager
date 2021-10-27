from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
import os
from re import search
import sqlite3
from validators import url

app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])


def get_db():
    return sqlite3.connect("/var/db/slackbot/cpp-bmstu.db")


@app.command("/check_me")
async def request_mentor(ack, respond, command):
    await ack()
    lab = command["text"][1:-1]
    if not url(lab) or search(
                r'https://github.com/bmstu-cbeer-2021-lab1/.*'
                '/pull/[0-9].*', lab) is None:
        await respond("Please send a valid url")
        return
    db = get_db()
    (mentor_tag, mentor_load) = db.execute(
            "SELECT TAG FROM mentors ORDER BY LOAD LIMIT 1").fetchone()
    db.execute(f"UPDATE mentors SET LOAD = {mentor_load + 1}"
               "WHERE TAG = {mentor_tag}")
    db.commit()
    sender_tag = command["user_id"]
    await app.client.conversations_open(users=mentor_tag)
    await app.client.chat_postMessage(
        channel=mentor_tag,
        text=f"<@{sender_tag}> <{lab}>"
    )
    await app.client.conversations_open(users=sender_tag)
    await app.client.chat_postMessage(
        channel=mentor_tag,
        text=f"<{lab}> was assigned to mentor <@{mentor_tag}>"
    )
    await respond(f"<{lab}> was assigned to mentor <@{mentor_tag}>")


@app.command("/add_mentor")
async def add_mentor(ack, respond, command):
    await ack()
    if command["channel_name"] != "private":
        await respond("You're not authorized")
        return
    db = get_db()
    mentor_cnt = db.execute("SELECT COUNT(*) FROM mentors").fetchone()[0]
    mentor_id = command["user_id"]
    if (mentor_id,) not in db.execute("SELECT TAG FROM mentors").fetchall():
        db.execute(
            f"INSERT INTO mentors VALUES('{mentor_cnt}', '{mentor_id}', 0)")
        db.commit()
        await respond("Done")
    else:
        await respond("You're already in!")


async def main():
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    await handler.start_async()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
