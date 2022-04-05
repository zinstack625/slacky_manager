import slack_app
import dboper


@slack_app.app.command("/add_mentor")
async def add_mentor(ack, respond, command):
    await ack()
    if command["channel_name"] != "private":
        await respond("You're not authorized")
        return
    db = dboper.get_db()
    mentor_cnt = db.execute("SELECT COUNT(*) FROM mentors").fetchone()[0]
    mentor_id = command["user_id"]
    if (mentor_id,) not in db.execute("SELECT TAG FROM mentors").fetchall():
        db.execute(
            "INSERT INTO mentors VALUES(?, ?, 0)", (mentor_cnt, mentor_id))
        db.commit()
        await respond("Done")
    else:
        await respond("You're already in!")
