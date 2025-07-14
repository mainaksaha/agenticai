from arcadepy import Arcade

import os

os.environ['ARCADE_API_KEY'] = ''

API_KEY = os.environ['ARCADE_API_KEY'] 
USER_ID = ""

client = Arcade()

# Authorize the tool
auth_response = client.tools.authorize(
    tool_name="Arithmetic.SendDmToUser@0.1.0",
    user_id=USER_ID,
)

# Check if authorization is completed
if auth_response.status != "completed":
    print(f"Click this link to authorize: {auth_response.url}")

# Wait for the authorization to complete
auth_response = client.auth.wait_for_completion(auth_response)

if auth_response.status != "completed":
    raise Exception("Authorization failed")

print("🚀 Authorization successful!")

result = client.tools.execute(
    tool_name="Arithmetic.SendDmToUser@0.1.0",
    input={
        "user_name": "chakori mitra",
        "message": "test message"
    },
    user_id=USER_ID,
)

print(result)