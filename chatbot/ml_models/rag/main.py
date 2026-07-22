import os
from dotenv import load_dotenv

load_dotenv()
# Load the environment variables
hf_token = os.getenv("HF_TOKEN") 

print(os.getenv("GEMINI_API_KEY"))