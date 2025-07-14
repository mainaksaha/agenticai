from typing import Annotated
 
from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import Slack
from arcade_tdk.errors import RetryableToolError
from slack_sdk import WebClient

@tool(
    requires_auth=Slack(
        scopes=[
            "chat:write",
            "im:write",
            "users.profile:read",
            "users:read",
        ],
    )
)
def send_dm_to_user(
    context: ToolContext,
    user_name: Annotated[str, "The Slack username of the person you want to message"],
    message: Annotated[str, "The message you want to send"],
) -> Annotated[str, "A confirmation message that the DM was sent"]:
    """Send a direct message to a user in Slack."""
    slack_client = WebClient(token=context.authorization.token)
 
    # Retrieve the user ID based on username
    user_list_response = slack_client.users_list()
    user_id = None
    for user in user_list_response["members"]:

        if user["name"].lower() == user_name.lower():
            user_id = user["id"]
            break
    if not user_id:
        raise RetryableToolError(
            "User not found",
            developer_message=f"User with username '{user_name}' not found."
        )
 
    # Open a conversation and send the message
    im_response = slack_client.conversations_open(users=[user_id])
    dm_channel_id = im_response["channel"]["id"]
    slack_client.chat_postMessage(channel=dm_channel_id, text=message)
 
    return "DM sent successfully"