import os
from dotenv import load_dotenv
load_dotenv()
env_vars = dict(os.environ)

# Print all variables
for key, value in env_vars.items():
    if key == "GOOGLE_API_KEY":
        print("GOOGLE_API_KEY is set.")
        print(f"{key} = {value}")