from dotenv import load_dotenv
from upload_files_to_github import upload_files_to_github
import os

load_dotenv()


files = ["pack/test.txt"]
repo = os.getenv("GITHUB_REPO")
token = os.getenv("GITHUB_TOKEN")
branch = "main"
upload_files_to_github(files, repo, token, branch)