from dotenv import load_dotenv
import git
from pathlib import Path
import os
import datetime
import subprocess

base_dir = os.path.dirname(os.path.abspath(__file__))
minecraft_pack_path = os.path.join(base_dir, "..", "pack/ethis_resourcepack")
git_path = os.path.join(base_dir, "..", )
env_path = os.path.join(base_dir, "..", "..", ".env")

def update_env(highest_date: datetime.datetime):
    """Updates the .env file with a new highest date."""
    with open(env_path, "r+") as env:
        lines = [line for line in env if not line.strip().startswith("LAST_UPDATE")]
        env.seek(0)
        lines.append(f'\nLAST_UPDATE = "{str(highest_date)}"')
        env.writelines(lines)
        env.truncate()


def get_highest_date(file_dict: dict[str, datetime.datetime]) -> datetime.datetime:
    """Returns the highest date from a dict of filenames to datetimes."""
    if file_dict:
        return max(file_dict.values())
    return datetime.datetime.now()


def setup_remote(repo: git.Repo, github_token: str, github_repo: str) -> git.Remote:
    """Configures and returns the origin remote with auth token."""
    remote_url = f"https://x-access-token:{github_token}@github.com/{github_repo}.git"
    origin = repo.remote(name="origin")
    origin.set_url(remote_url)
    return origin


def safe_pull(repo: git.Repo, origin: git.Remote):
    """Discards local changes and pulls from remote cleanly."""
    # Hard reset staged/tracked changes
    repo.git.reset("--hard", "HEAD")
    # Remove untracked files and directories (except the pack folder)
    repo.git.clean("-fd", "--exclude=pack/")
    print("reset local changes")

    origin.pull()
    print("pulled origin")


def get_last_update() -> datetime.datetime:
    """Reads LAST_UPDATE from env, sets it to now if missing, raises KeyError."""
    prev_highest_date = os.getenv("LAST_UPDATE")
    if not prev_highest_date:
        update_env(datetime.datetime.now())
        raise KeyError("LAST_UPDATE is not set in .env, set current time as highest.")
    return datetime.datetime.strptime(prev_highest_date, "%Y-%m-%d %H:%M:%S.%f")


def collect_changed_files(since: datetime.datetime) -> tuple[list[str], dict[str, datetime.datetime]]:
    """Scans the pack directory and returns files changed since the given datetime."""
    p = Path(minecraft_pack_path)
    files_dict = {}
    changed_files = []
    for f in p.rglob("*"):
        if f.is_file():
            file = str(f)
            datestamp = datetime.datetime.fromtimestamp(os.path.getmtime(f))
            files_dict[file] = datestamp
            if datestamp > since:
                changed_files.append(file)
    return changed_files, files_dict


def commit_and_push(repo: git.Repo, files: list[str], remote_url: str):
    """Stages, commits, and pushes the given files."""
    repo.index.add(files)
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


def upload_files():
    """Syncs the repository to GitHub if there are any changes."""
    load_dotenv(env_path)
    print("loaded env")

    github_token = os.getenv("GITHUB_TOKEN")
    github_repo = os.getenv("GITHUB_REPO")
    print("tokens loaded")

    repo = git.Repo(git_path)
    if not github_token or not github_repo:
        raise LookupError("Git tokens not found")
    origin = setup_remote(repo, github_token, github_repo)
    safe_pull(repo, origin)

    last_update = get_last_update()

    changed_files, files_dict = collect_changed_files(since=last_update)
    update_env(get_highest_date(files_dict))
    print("updated env")
    print(changed_files)

    if changed_files:
        commit_and_push(repo, changed_files, origin.url)


if __name__ == "__main__":
    upload_files()