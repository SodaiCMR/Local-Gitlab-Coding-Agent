import os
from dotenv import load_dotenv

load_dotenv()

GITLAB_URL = os.getenv("GITLAB_URL")
GITLAB_PRIVATE_TOKEN = os.getenv("GITLAB_PRIVATE_TOKEN")
GITLAB_PROJECT_ID = os.getenv("GITLAB_PROJECT_ID")