from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
import os
from re import search
import sqlite3
from validators import url

app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])


def get_db():
    return sqlite3.connect("/var/db/slackbot/cpp-bmstu.db")
    # return sqlite3.connect("cpp-bmstu.db")


def get_blocks(sender_tag, lab):
    return [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"<@{sender_tag}> <{lab}>"
        },
        "accessory": {
            "type": "checkboxes",
            "action_id": "approved",
            "options": [{
                "value": "is_approved",
                "text": {
                    "type": "plain_text",
                    "text": "Approved"
                }
            }],
            "confirm": {
                "title": {
                    "type": "plain_text",
                    "text": "Confirmation"
                },
                "text": {
                    "type": "plain_text",
                    "text": "Are you sure?"
                },
                "confirm": {
                    "type": "plain_text",
                    "text": "Yes"
                },
                "deny": {
                    "type": "plain_text",
                    "text": "No"
                }
            }
        }
    }]


@app.action("approved")
async def approve_lab(ack, body, payload):
    await ack()
    # it's easy enough to pull the id from the request body
    checker_tag = body["user"]["id"]
    db = get_db()
    # let's assume that if loop is not entered, all checkmarks are
    # disabled, thus lab was unapproved, that's why here it's + 1
    # over what's been before
    checker_load = db.execute(
        "SELECT LOAD FROM mentors WHERE TAG = ?", (checker_tag,)
    ).fetchone()[0] + 1
    for i in payload["selected_options"]:
        if i["value"] == "is_approved":
            # and here, because of the beforementioned assumption,
            # we have to substract 2 instead of 1. that's jank tbh
            checker_load -= 2

    db.execute("UPDATE mentors SET LOAD = ? "
               "WHERE TAG = ?", (checker_load, checker_tag))
    db.commit()


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
        "SELECT TAG, LOAD FROM mentors ORDER BY LOAD LIMIT 1").fetchone()
    # even though logically it'd be better to place this after the
    # designation reply, I want to finish working with the db asap
    db.execute("UPDATE mentors SET LOAD = ? "
               "WHERE TAG = ?", (mentor_load + 1, mentor_tag))
    db.commit()
    sender_tag = command["user_id"]
    # frontend boilerplate
    mentor_dm_blocks = get_blocks(sender_tag, lab)
    await app.client.conversations_open(users=mentor_tag)
    await app.client.chat_postMessage(
        channel=mentor_tag,
        blocks=mentor_dm_blocks,
        # text block is still used for notifications and other places
        # where it's impossible to show actions
        text="You've got a new lab to check!"
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
            "INSERT INTO mentors VALUES(?, ?, 0)", (mentor_cnt, mentor_id))
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
