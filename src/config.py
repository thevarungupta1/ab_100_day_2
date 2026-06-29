import os
from dotenv import load_dotenv

load_dotenv()

AZURE_AI_ENDPOINT = os.getenv("AZURE_AI_ENDPOINT")
AZURE_AI_KEY = os.getenv("AZURE_AI_KEY")

PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "gpt-4.1")
REASONING_MODEL = os.getenv("REASONING_MODEL", "gpt-5.2")
FAST_MODEL = os.getenv("FAST_MODEL", "gpt-4.1")