import sqlite3
from os import environ


def get_db():
    if environ["DEBUG"] == 1:
        return sqlite3.connect("/var/db/slackbot/cpp-bmstu.db")
    return sqlite3.connect("cpp-bmstu.db")


async def update_mentor_load(mentor_tag, amount=0):
    db = get_db()
    mentor_load = db.execute(
        "SELECT LOAD FROM mentors WHERE TAG = ?", (mentor_tag,)
    ).fetchone()[0] - amount
    db.execute("UPDATE mentors SET LOAD = ? "
               "WHERE TAG = ?", (mentor_load, mentor_tag))
    db.commit()


async def distribute_lab():
    db = get_db()
    (mentor_tag, mentor_load) = db.execute(
        "SELECT TAG, LOAD FROM mentors ORDER BY LOAD LIMIT 1").fetchone()
    # even though logically it'd be better to place this after the
    # designation reply, I want to finish working with the db asap
    db.execute("UPDATE mentors SET LOAD = ? "
               "WHERE TAG = ?", (mentor_load + 2, mentor_tag))
    db.commit()
    return mentor_tag


def check_admin(tag):
    db = get_db()
    (result,) = db.execute("SELECT EXISTS(SELECT * FROM admins WHERE TAG=?)", (tag,)).fetchone()
    if result == 0 and db.execute("SELECT * FROM admins").fetchone() is None:
        return True
    elif result == 0:
        return False
    else:
        return True


async def init_db():
    db = get_db()
    db.execute("CREATE TABLE IF NOT EXISTS mentors(ID INT PRIMARY KEY NOT NULL, TAG TEXT NOT NULL, LOAD INT DEFAULT 0)")
    db.execute("CREATE TABLE IF NOT EXISTS admins(ID INT PRIMARY KEY NOT NULL, TAG TEXT NOT NULL, PRIORITY INT DEFAULT 0)")
