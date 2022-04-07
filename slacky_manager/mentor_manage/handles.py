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
        (mentor_load,) = db.execute("SELECT AVG(LOAD) from mentors").fetchone()
        if mentor_load is None:
            mentor_load = 0
        db.execute(
            "INSERT INTO mentors VALUES(?, ?, ?)",
            (mentor_cnt, mentor_id, int(mentor_load),))
        db.commit()
        await respond("Done")
    else:
        await respond("You're already in!")


@slack_app.app.command("/remove_mentor")
async def remove_mentor(ack, respond, command):
    await ack()
    if command["channel_name"] != "private":
        await respond("Must be called in private chat")
        return
    if not dboper.check_admin(command["user_id"]):
        await respond("You're not the admin")
        return
    # mentor_id is expected to be member id and not a mention
    # if someone can fix that, that'd be nice
    mentor_id = command["text"]
    db = dboper.get_db()
    if db.execute("SELECT EXISTS(SELECT * FROM mentors where TAG=?)",
                  (mentor_id,)).fetchone() == (1,):
        db.execute("DELETE FROM mentors WHERE TAG=?", (mentor_id,))
        db.commit()
        await respond("Done")
    else:
        await respond("There is no such mentor!")
