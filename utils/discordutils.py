import discord
import json
import os

async def create_thread(author: discord.User, channel: discord.TextChannel, name):
    thread = await channel.create_thread(name=name, message=None)
    if not thread:
        return
    await thread.send(content=f"{author.mention} please follow the instructions below.")
    save_thread_owner(thread, author)
    return thread

def get_thread_owner(thread_id) -> int:
    """Returns owner id of a given thread_id

    Args:
        thread_id (int): the id of the query thread

    Returns:
        int: owner_id or 0 if not found
    """
    if os.path.exists("threadowners.json"):
        with open("threadowners.json", "r") as f:
            thread_owners = json.load(f)
        try:
            owner_id = thread_owners[str(thread_id)]
            return owner_id
        except: # noqa: E722
            return 0
    return 0

def save_thread_owner(thread, author):
    if os.path.exists("threadowners.json"):
        with open("threadowners.json", "r") as f:
            thread_owners = json.load(f)
    else:
        thread_owners = {}

    thread_owners[str(thread.id)] = author.id
    with open("threadowners.json", "w") as f:
        json.dump(thread_owners, f, indent=2)
        
def decide_action(message: discord.Message)-> tuple[int, str]:
    """decides the action 

    Args:
        content (str): message content

    Returns:
        tuple: action, reason [0, 1, 2] error; png; json, reason
    """
    if len(message.attachments) > 1:
        return 0, "Please only attach one file."
    for file in message.attachments:
        if file.filename.endswith("png"):
            return 1, ""
        if file.filename.endswith("json"):
            return 2, ""
        
    return 0, f"File type {file.filename[file.filename.rfind("."):]} not supported." # type: ignore
    
    
def verify_owner(message: discord.Message) -> bool:
    owner_id = get_thread_owner(message.channel.id)
    if message.author.id == owner_id:
        return True
    else:
        return False 
    
    
def download_file(attachment):
    pass

def move_file(idk): 
    pass

def setup_model(idk):
    pass