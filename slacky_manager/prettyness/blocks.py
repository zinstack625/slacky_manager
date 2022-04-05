CONFIRM_BLOCK = {
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


def get_revise_blocks(textbox):
    return [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": textbox
        },
    },
    {
        "type": "actions",
        "elements": [{
            "type": "checkboxes",
            "action_id": "revise",
            "options": [{
                "text": {
                    "type": "plain_text",
                    "text": "Approved",
                    },
                "value": "revise"
            }],
            "initial_options": [{
                "text": {
                    "type": "plain_text",
                    "text": "Approved",
                    },
                "value": "revise"
            }],
            "confirm": CONFIRM_BLOCK
        }]
    }]


def get_appr_blocks(textbox):
    return [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": textbox
        },
    },
    {
        "type": "actions",
        "elements": [{
            "type": "checkboxes",
            "action_id": "approved",
            "options": [{
                "text": {
                    "type": "plain_text",
                    "text": "Approved",
                    },
                "value": "approve"
            }],
            "confirm": CONFIRM_BLOCK
        },
        {
            "type": "button",
            "action_id": "deny",
            "style": "danger",
            "text": {
                "type": "plain_text",
                "text": "Stop checking"
            },
            "confirm": CONFIRM_BLOCK
        }]
    }]


