import slack_app
from dboper import update_mentor_load, add_done_lab, remove_done_lab
from asyncio import create_task
from prettyness.blocks import get_appr_blocks, get_revise_blocks
from re import match, findall


@slack_app.app.action("approved")
async def approve_lab(ack, body, respond):
    await ack()
    message_text = body["message"]["blocks"][0]["text"]["text"]
    sender_tag_match = match(r'(<@.*>) .*', message_text)
    sender_tag = sender_tag_match.group(1)
    task_sender_name = create_task(
        slack_app.app.client.users_profile_get(user=sender_tag[2:-1])
    )
    link_match = match(r'<@.*> <(.*)>', message_text)
    link = link_match.group(1)
    sender_name = await task_sender_name
    task_db_save = create_task(
        add_done_lab(sender_name['profile']['real_name'], link)
    )
    checker_tag = body["user"]["id"]
    task_load = create_task(
        update_mentor_load(checker_tag, -1)
    )
    # the same for message blocks
    msg_blocks = get_revise_blocks(message_text)
    db_save_result = await task_db_save
    task_respond = None
    if not db_save_result:
        msg_blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Something went wrong with adding done lab to \
database, please make sure to report it manually"
                }
            })
    task_respond = create_task(
        respond(replace_original=True, blocks=msg_blocks)
    )
    await task_load
    await task_respond


@slack_app.app.action("revise")
async def revise_lab(ack, body, respond):
    await ack()
    message_text = body["message"]["blocks"][0]["text"]["text"]
    link_match = match(r'<@.*> <(.*)>', message_text)
    link = link_match.group(1)
    task_db_remove = create_task(
        remove_done_lab(link)
    )
    checker_tag = body["user"]["id"]
    task_load = create_task(
        update_mentor_load(checker_tag, 1)
    )
    msg_blocks = get_appr_blocks(message_text)
    task_respond = create_task(
        respond(replace_original=True, blocks=msg_blocks)
    )
    await task_db_remove
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
