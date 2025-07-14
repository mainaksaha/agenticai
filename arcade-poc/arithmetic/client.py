from arcadepy import Arcade
import os

os.environ['ARCADE_API_KEY'] = ''

API_KEY = os.environ['ARCADE_API_KEY'] 
USER_ID = ""

client = Arcade()

result = client.tools.execute(
    tool_name="Arithmetic.SayHello@0.1.0",
    input={
        "owner": "ArcadeAI",
        "name": "arcade-ai",
        "starred": "true"
    },
    user_id=USER_ID,
)

print(result)