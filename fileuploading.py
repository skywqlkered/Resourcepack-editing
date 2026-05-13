from dotenv import load_dotenv
import git
from pathlib import Path
import os 
import datetime

def update_env(highest_date: datetime.datetime):
    with open(".env", "r+") as env:
            lines = [line for line in env if not line.strip().startswith("LAST_UPDATE")]
            env.seek(0)
            lines.append(f'LAST_UPDATE = "{str(highest_date)}"')
            env.writelines(lines)
            env.truncate()

def get_highest_date(file_dict: dict[str, datetime.datetime]) -> datetime.datetime:
    if file_dict:
        highest_date = list(file_dict.values())[0]
        for date in file_dict.values():
            if date > highest_date:
                highest_date = date
    else: 
        highest_date = datetime.datetime.now()
    return highest_date

def upload_files():
    repo = git.Repo("../resourcepack-editing")# initialize
    origin = repo.remote(name='origin') #set remote
    origin.pull() # pull
    load_dotenv()
    prev_highest_date = os.getenv("LAST_UPDATE")
    format = "%Y-%m-%d %H:%M:%S.%f"
    if prev_highest_date:
        datetime_str = datetime.datetime.strptime(prev_highest_date, format)
    else: 
        update_env(datetime.datetime.now())
        raise KeyError("LAST_UPDATE is not set in .env, set current time as highest.")
    
    
    upload_files = []
    p = Path(r"pack/ethis_resourcepack")
    files_dict = {}
    for f in p.rglob("*"):
        if f.is_file():
            file = str(f)
            timestamp = os.path.getmtime(f)
            datestamp = datetime.datetime.fromtimestamp(timestamp)
            files_dict[file] = datestamp
            if datestamp > datetime_str:
                upload_files.append(file)
    highest_date = get_highest_date(files_dict)
    update_env(highest_date)
    
    if upload_files:
        repo.index.add(upload_files) #add 
        repo.index.commit("Resourcepack update") # commit
        origin.push()# push
    else: print("No files were uploaded")
    
if __name__ == "__main__":
    upload_files()