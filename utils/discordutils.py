import discord
import json
import os
from pathlib import Path
from fileformatting import check_item, add_model_to_existing_item, add_model_to_new_item, create_painting_model

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
    
    
def verify_owner(channel, author: discord.User | discord.Member) -> bool:
    owner_id = get_thread_owner(channel.id)
    if author.id == owner_id:
        return True
    else:
        return False 

async def download_texture(message: discord.Message):
    attachment = message.attachments[0]#type: ignore
    path = Path("pack/ethis_resourcepack/assets/minecraft/textures/item/" + attachment.filename)
    update_thread_content(message.channel.id, texture=attachment.filename)
    await attachment.save(fp=path) 
    
async def download_model(message: discord.Message):
    attachment = message.attachments[0]#type: ignore
    path = Path("pack/ethis_resourcepack/assets/minecraft/models/item/" + attachment.filename)
    update_thread_content(message.channel.id, model=attachment.filename)
    await attachment.save(fp=path) 

def get_thread_content(threadid: int) -> dict | None:
    with open("threadcontent.json", "r") as file:
        data = json.load(file)

        for thread in data["threads"]:
            if list(thread.keys())[0] == str(threadid):
                return list(thread.values())[0]
    
        return None

def update_thread_content(threadid: int, **kwargs):
    texture = kwargs.get("texture", None)
    model = kwargs.get("model", None)
    owner = kwargs.get("owner", None)
    treshold = kwargs.get("treshold", None)
    mcitem = kwargs.get("mcitem", None)
    
    contents = {"textures": texture, "model": model, "owner":owner, "treshold":treshold, "mcitem": mcitem}
    
    entry = get_thread_content(threadid)
    if entry: # edit
        for key, val in contents.items():
            if val and not entry[key] and key != "textures":
                entry[key] = val 
            elif key == "textures":
                if val not in entry["textures"] and val:
                    entry["textures"].append(val)
    else: # new
        entry = {
        "owner": owner,
        "textures":[texture],
        "model": model,
        "mcitem": mcitem,
        "threshold": treshold
        }
    
    with open("threadcontent.json", "r") as f:
        data = json.load(f)
        
        for thread in data["threads"]:
            if list(thread.keys())[0] == str(threadid):
                old_entry = list(thread.values())[0]
        try:
            data["threads"].remove({str(threadid): old_entry}) # type: ignore
        except ValueError:
            pass
        except UnboundLocalError:
            pass
        
    data["threads"].append({threadid: entry})

    with open("threadcontent.json", "w") as f:
        json_str = json.dumps(data, indent=4)
        f.write(json_str)


def verify_uploads(threadid:int) -> bool | list | None:
    with open("threadcontent.json", "r") as f:
        data = json.load(f)
    
    entry = None
    
    for thread in data["threads"]:
        if list(thread.keys())[0] == str(threadid):
            entry = list(thread.values())[0]
    
    bools = {}
    
    if not entry:
        return
    
    for key, val in entry.items():
        if key == "textures":
            if len(val) != 0:
                bools[key] = True
            else:
                bools[key] = False
        elif key == "threshold":
            continue
        else:
            if val:
                bools[key] = True
            else:
                bools[key] = False
                
    if all(list(bools.values())):
        return True
    else:
        false_list = []
        for key,val in bools.items():
            if not val:
                false_list.append(key)
        return false_list

def create_texture(threadid: int):
    path = "pack/ethis_resourcepack/assets/minecraft/items/"
    
    
    with open("threadcontent.json", "r") as f:
        data = json.load(f)
    entry = None
    for thread in data["threads"]:
        if list(thread.keys())[0] == str(threadid):
            entry = list(thread.values())[0]
    if not entry:
        return
    
    mcitem = entry["mcitem"]
    modelname = entry["model"].removesuffix(".json")
    if check_item(path, mcitem):
        treshold = add_model_to_existing_item(path, mcitem, modelname)
    else:
        treshold = add_model_to_new_item(path, mcitem, modelname)
        
    return treshold

def create_painting():
    create_painting_model()