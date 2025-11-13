from sbcommons.messaging import webhooks


def send_message(webhook_url: str, title: str, msg: str) -> bool:
    """
    Send a message to Microsoft Teams using Adaptive Cards format.
    
    Args:
        webhook_url: The MS Teams webhook URL
        title: The title of the message
        msg: The message content (supports markdown)
    
    Returns:
        bool: True if successful, False otherwise
    """
    data = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": title,
                            "weight": "bolder",
                            "size": "large",
                            "wrap": True
                        },
                        {
                            "type": "TextBlock",
                            "text": msg,
                            "wrap": True
                        }
                    ]
                }
            }
        ]
    }

    return webhooks.post_to_webhook(service='teams', webhook_url=webhook_url, json=data)
