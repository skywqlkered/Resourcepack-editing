from dotenv import load_dotenv
import git
from pathlib import Path
import os
import datetime
import subprocess
base_dir = os.path.dirname(os.path.abspath(__file__))  # resolves to .../utils/
minecraft_pack_path  = os.path.join(base_dir, "..", "pack/ethis_resourcepack")
git_path = os.path.join(base_dir, "..", )
env_path = os.path.join(base_dir, "..", "..", ".env")  # utils/ -> Resourcepack-editing/ -> home/container/

def update_env(highest_date: datetime.datetime):
    """Updates the .env file with a new highest date

    Args:
        highest_date (datetime.datetime): The new date to be added
    """
    with open(env_path, "r+") as env:
        lines = [line for line in env if not line.strip().startswith("LAST_UPDATE")]
        env.seek(0)
        lines.append(f'\nLAST_UPDATE = "{str(highest_date)}"')
        env.writelines(lines)
        env.truncate()


def get_highest_date(file_dict: dict[str, datetime.datetime]) -> datetime.datetime:
    """Returns the highest date stored in the .env file.

    Args:
        file_dict (dict[str, datetime.datetime]): dict of file names and latest changed date as values.

    Returns:
        datetime.datetime: The most recest date in datetime format
    """
    if file_dict:
        highest_date = list(file_dict.values())[0]
        for date in file_dict.values():
            if date > highest_date:
                highest_date = date
    else:
        highest_date = datetime.datetime.now()
    return highest_date


def upload_files():
    """Syncs the repository to github if there are any changes.

    Raises:
        KeyError: raises when LAST_UPDATE is not defined in the env 
    """
    load_dotenv(env_path)
    print("loaded env")
    github_token = os.getenv("GITHUB_TOKEN")
    github_repo = os.getenv("GITHUB_REPO")  # e.g. "skywqlkered/Resourcepack-editing"
    print("tokens loaded")
    repo = git.Repo(git_path)
    remote_url = f"https://x-access-token:{github_token}@github.com/{github_repo}.git"
    origin = repo.remote(name="origin")
    origin.set_url(remote_url)
    origin.pull()
    print("pulled origin")
    prev_highest_date = os.getenv("LAST_UPDATE")
    format = "%Y-%m-%d %H:%M:%S.%f"
    if prev_highest_date:
        datetime_str = datetime.datetime.strptime(prev_highest_date, format)
    else:
        update_env(datetime.datetime.now())
        raise KeyError("LAST_UPDATE is not set in .env, set current time as highest.")

    uploaded_files = []
    p = Path(minecraft_pack_path)
    files_dict = {}
    for f in p.rglob("*"):
        if f.is_file():
            file = str(f)
            timestamp = os.path.getmtime(f)
            datestamp = datetime.datetime.fromtimestamp(timestamp)
            files_dict[file] = datestamp
            if datestamp > datetime_str:
                uploaded_files.append(file)
    highest_date = get_highest_date(files_dict)
    update_env(highest_date)
    print("updated env")
    print(uploaded_files)
    if uploaded_files:
        repo.index.add(uploaded_files)
        repo.index.commit("Resourcepack update")
        print("pushing")
        result = subprocess.run(
            ["git", "push", remote_url],
            cwd=git_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        print(f"returncode: {result.returncode}")


if __name__ == "__main__":
    upload_files()
