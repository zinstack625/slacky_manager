import slack_app
from re import search
from validators import url
from dboper import distribute_lab
from prettyness.blocks import get_appr_blocks
from asyncio import create_task


@slack_app.app.command("/check_me")
async def request_mentor(ack, respond, command):
    await ack()
    lab = command["text"][1:-1]
    if not url(lab) or search(
        r'https://github.com/bmstu-cbeer-2021-lab1/.*'
            '/pull/[0-9].*', lab) is None:
        await respond("Please send a valid url")
        return
    mentor_tag = await distribute_lab()
    sender_tag = command["user_id"]
    # frontend boilerplate
    mentor_dm_blocks = get_appr_blocks(f"<@{sender_tag}> <{lab}>")
    await slack_app.app.client.conversations_open(users=mentor_tag)
    task_msg_mentor = create_task(
        slack_app.app.client.chat_postMessage(
            channel=mentor_tag,
            blocks=mentor_dm_blocks,
            # text block is still used for notifications and other places
            # where it's impossible to show actions
            text="You've got a new lab to check!"
        )
    )
    await slack_app.app.client.conversations_open(users=sender_tag)
    task_msg_submitter = create_task(
        slack_app.app.client.chat_postMessage(
            channel=sender_tag,
            text=f"<{lab}> was assigned to mentor <@{mentor_tag}>"
        )
    )
    task_respond = create_task(
        respond(f"<{lab}> was assigned to mentor <@{mentor_tag}>")
    )
    await task_msg_mentor
    await task_msg_submitter
    await task_respond
