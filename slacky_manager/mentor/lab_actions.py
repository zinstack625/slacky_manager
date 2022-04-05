import slack_app
from dboper import update_mentor_load
from asyncio import create_task
from prettyness.blocks import get_appr_blocks, get_revise_blocks
from re import findall


@slack_app.app.action("approved")
async def approve_lab(ack, body, respond):
    await ack()
    # it's easy enough to pull the id from the request body
    checker_tag = body["user"]["id"]
    task_load = create_task(
        update_mentor_load(checker_tag, -1)
    )
    # the same for message blocks
    msg_blocks = get_revise_blocks(
        body["message"]["blocks"][0]["text"]["text"])
    task_respond = create_task(
        respond(replace_original=True, blocks=msg_blocks)
    )
    await task_load
    await task_respond


@slack_app.app.action("revise")
async def revise_lab(ack, body, respond):
    await ack()
    checker_tag = body["user"]["id"]
    task_load = create_task(
        update_mentor_load(checker_tag, 1)
    )
    msg_blocks = get_appr_blocks(
        body["message"]["blocks"][0]["text"]["text"])
    task_respond = create_task(
        respond(replace_original=True, blocks=msg_blocks)
    )
    await task_load
    await task_respond


@slack_app.app.action("deny")
async def deny_lab(ack, body, respond):
    await ack()
    task_respond = create_task(
        respond(delete_original=True)
    )
    checker_tag = body["user"]["id"]
    task_load = create_task(
        update_mentor_load(checker_tag, -2)
    )
    message_body = body["message"]["blocks"][0]["text"]["text"]
    sender_tag = findall(r"<@.*> ", message_body)[0][2:-2]
    lab = findall(r" <.*>", message_body)[0][2:-1]
    await slack_app.app.client.conversations_open(users=sender_tag)
    task_msg_post = create_task(
        slack_app.app.client.chat_postMessage(
            channel=sender_tag,
            text=f"<@{checker_tag}> stopped checking lab <{lab}>"
        )
    )
    await task_load
    await task_msg_post
    await task_respond
