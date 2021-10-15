from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
# from logic import *
import os
import sqlite3

app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])
count = 0


def pull_mentors_from_db():
    db = sqlite3.connect("cpp-bmstu.db")
    return db.execute("SELECT TAG FROM mentors").fetchall()


@app.command("/ping")
async def pong(ack, say, command):
    await ack()
    print("got a command")
    await say("Pong")


@app.command("/check_me")
async def request_mentor(ack, respond, command):
    await ack()
    lab = command["text"]
    mentors = pull_mentors_from_db()
    mentor_tag = mentors[count][0]
    await app.client.conversations_open(users=mentor_tag)
    await app.client.chat_postMessage(
        channel=mentor_tag,
        text=lab
    )
    await respond(f"{lab} was assigned to mentor <@{mentor_tag}>")


@app.message("Hello")
async def hello(message, say):
    print("boring message")
    say("hello...")


@app.command("/add_mentor")
async def add_mentor(ack, respond, command):
    await ack()
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
