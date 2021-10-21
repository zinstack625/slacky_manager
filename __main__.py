from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
import os
from re import search
import sqlite3
from validators import url

app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])
count = 0


def pull_mentors_from_db():
    db = sqlite3.connect("cpp-bmstu.db")
    return db.execute("SELECT TAG FROM mentors").fetchall()


@app.command("/check_me")
async def request_mentor(ack, respond, command):
    await ack()
    lab = command["text"][1:-1]
    if not url(lab) or search(r'https://github.com/bmstu-cbeer-2021-lab1/.*/pull/[0-9].*', lab) is None:
        await respond("Please send a valid url")
        return
    mentors = pull_mentors_from_db()
    global count
    mentor_tag = mentors[count][0]
    sender_tag = command["user_id"]
    await app.client.conversations_open(users=mentor_tag)
    await app.client.chat_postMessage(
        channel=mentor_tag,
        text=f"<@{sender_tag}> <{lab}>"
    )
    db = sqlite3.connect("cpp-bmstu.db")
    count = (
        count + 1) % db.execute("SELECT COUNT(*) FROM mentors").fetchall()[0][0]
    await respond(f"<{lab}> was assigned to mentor <@{mentor_tag}>")


@app.command("/add_mentor")
async def add_mentor(ack, respond, command):
    await ack()
    if command["channel_name"] != "private":
        await respond("You're not authorized")
        return
    db = sqlite3.connect("cpp-bmstu.db")
    mentor_cnt = db.execute("SELECT COUNT(*) FROM mentors").fetchall()[0][0]
    mentor_id = command["user_id"]
    if (mentor_id,) not in db.execute("SELECT TAG FROM mentors").fetchall():
        db.execute(
            f"INSERT INTO mentors VALUES('{mentor_cnt}', '{mentor_id}', NULL)")
        await respond("Done")
    else:
        await respond("You're already in!")
    db.commit()


async def main():
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    await handler.start_async()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
