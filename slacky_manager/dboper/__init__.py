import sqlite3
from re import match
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


async def add_done_lab(tag, link):
    db = get_db()
    print(link)
    regmatch = match(r'https://github.com/bmstu-cbeer-2021-lab1/[0-9]{2}-lab-([0-9]{2}).*', link)
    if match is None:
        return False
    lab_num = regmatch.group(1)
    lab_cnt = db.execute("SELECT COUNT(*) FROM done_labs").fetchone()[0]
    db.execute('INSERT INTO done_labs VALUES(?, ?, ?, ?)',
               (lab_cnt, tag, link, lab_num))
    db.commit()
    return True


async def remove_done_lab(link):
    db = get_db()
    db.execute('DELETE FROM done_labs WHERE LINK=?', (link,))
    db.commit()


async def init_db():
    db = get_db()
    db.execute("CREATE TABLE IF NOT EXISTS mentors(\
        ID INT PRIMARY KEY NOT NULL,\
        TAG TEXT NOT NULL,\
        LOAD INT DEFAULT 0)")
    db.execute("CREATE TABLE IF NOT EXISTS admins(\
        ID INT PRIMARY KEY NOT NULL,\
        TAG TEXT NOT NULL,\
        PRIORITY INT DEFAULT 0)")
    db.execute("CREATE TABLE IF NOT EXISTS done_labs(\
        ID INT PRIMARY KEY NOT NULL,\
        TAG TEXT NOT NULL,\
        LINK TEXT NOT NULL,\
        LAB INT NOT NULL)")


async def get_lab_table():
    db = get_db()
    table = {'table': []}
    for student, lab in db.execute('SELECT TAG, LAB from done_labs'):
        cur = None
        for i, entry in enumerate(table['table']):
            if entry['name'] == student:
                cur = i
                break
        if cur is not None:
            table['table'][cur]['labs'].append(lab)
        else:
            table['table'].append({
                'name': student,
                'labs': [lab],
            })
    for i in table['table']:
        i['labs'].sort()
    table['table'].sort(key=lambda x: x['name'])
    return table