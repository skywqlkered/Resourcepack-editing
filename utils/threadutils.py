import discord
import json
import os
from pathlib import Path
from .modelutils import (
    check_item,
    add_model_to_existing_item,
    add_model_to_new_item,
    create_painting_model,
    create_textures_folder,
    edit_model_paths,
)
import regex as re
import datetime
import shutil

base_dir = os.path.dirname(os.path.abspath(__file__))  # resolves to .../utils/

thread_content_path = os.path.join(base_dir, "..", "threadcontent.json")
thread_owners_path  = os.path.join(base_dir, "..", "threadowners.json")
minecraft_pack_path = os.path.join(base_dir, "../","../", "server-resource-pack/ethis_resourcepack")

async def create_thread(author: discord.User, channel: discord.TextChannel, name):
    thread = await channel.create_thread(name=name, message=None)
    if not thread:
        return
    await thread.send(
        content=f"{author.mention} please follow the instructions in <#1518953357941932183>."
    )
    save_thread_owner(thread, author)
    return thread


async def send_texture(thread: discord.Thread, post_channel_id):
    entry = get_entry(threadid=thread.id)
    if not entry:
        return

    real_textures = []
    for texture in entry["textures"]:
        if texture:
            real_textures.append(texture)

    texture_str = ", ".join(real_textures)

    channel = await thread.guild.fetch_channel(post_channel_id)
    message_sent = await channel.send(f"{entry["owner"]} Uploaded\n{entry["model"]} with textures: {texture_str}")  # type: ignore
    update_thread_content(thread.id, message_id=message_sent.id)


async def close_thread(thread: discord.Thread, post_channel_id):
    await thread.edit(locked=True)
    await thread.send(
        "Thank You for using the texture creator today. Enjoy your custom model!"
    )
    await send_texture(thread=thread, post_channel_id=post_channel_id)


async def delete_thread(thread: discord.Thread):
    entry = get_entry(thread.id)
    if not entry:
        return

    try:
        # Delete texture folder
        thread_name = entry["thread_name"]
        shutil.rmtree(minecraft_pack_path + "textures/item/" + thread_name)
    except Exception as eerror:
        print("Delete texture folder " + str(eerror))
    try:
        model_name = entry["model"]
        os.remove(minecraft_pack_path + "models/item/" + model_name)
    except Exception as eerror:
        print("Delete model  " + str(eerror))
    try:
        # delete thread
        await thread.delete()
        update_thread_content(threadid=thread.id, isDeleted=True)
    except Exception as eerror:
        print("Delete thread " + str(eerror))

    # return message id for deletion
    return entry["message_id"]

def get_thread_owner(thread_id) -> int:
    """Returns owner id of a given thread_id

    Args:
        thread_id (int): the id of the query thread

    Returns:
        int: owner_id or 0 if not found
    """
    if os.path.exists(thread_owners_path):
        with open(thread_owners_path, "r") as f:
            thread_owners = json.load(f)
        try:
            owner_id = thread_owners[str(thread_id)]["author"]
            return owner_id
        except:  # noqa: E722
            return 0
    return 0


def save_thread_owner(thread, author):
    if os.path.exists(thread_owners_path):
        with open(thread_owners_path, "r") as f:
            thread_owners = json.load(f)
    else:
        thread_owners = {}

    thread_owners[str(thread.id)] = {
        "author": author.id,
        "date": datetime.datetime.now().isocalendar().week,
    }
    with open(thread_owners_path, "w") as f:
        json.dump(thread_owners, f, indent=2)

def delete_thread_owner(thread):

    with open(thread_owners_path, "r") as f:
        thread_owners:dict = json.load(f)

    thread_owners.pop(str(thread.id))
    with open(thread_owners_path, "w") as f:
        json.dump(thread_owners, f, indent=2)

def decide_action(message: discord.Message) -> tuple[int, str]:
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
        if file.filename.endswith("mcmeta"):
            return 3, ""

    return 0, f"File type {file.filename[file.filename.rfind("."):]} not supported."  # type: ignore


def verify_owner(channel, author: discord.User | discord.Member) -> bool:
    owner_id = get_thread_owner(channel.id)
    if author.id == owner_id:
        return True
    else:
        return False


async def verify_thread(interaction: discord.Interaction):
    if not verify_owner(interaction.channel, author=interaction.user):  # noqa: F405
        await interaction.response.send_message(
            "This isn't your thread.", ephemeral=True
        )
        return False
    if not isinstance(interaction.channel, discord.Thread):
        await interaction.response.send_message(
            "This command can only be used in a texture thread.", ephemeral=True
        )
        return False
    return True


async def download_texture(message: discord.Message):
    entry = get_entry(message.channel.id)
    print(entry)
    if not entry:
        return None

    isPainting = entry["isPainting"]
    modelname = entry["model"]
    thread_name = entry["thread_name"]
    create_textures_folder(thread_name=thread_name)

    attachment = message.attachments[0]  # type: ignore

    if isPainting and modelname:
        path = Path(
            minecraft_pack_path + "/textures/item/"
            + thread_name
            + "/"
            + modelname.removesuffix(".json")
            + ".png"
        )
    else:
        path = Path(
            minecraft_pack_path + "textures/item/"
            + thread_name
            + "/"
            + attachment.filename
        )
    update_thread_content(message.channel.id, texture=attachment.filename)
    await attachment.save(fp=path)


async def download_model(message: discord.Message):
    attachment = message.attachments[0]  # type: ignore
    path = Path(
        minecraft_pack_path + "models/item/" + attachment.filename
    )
    update_thread_content(message.channel.id, model=attachment.filename)
    
    entry = get_entry(message.channel.id)
    if not entry:
        return
    
    await attachment.save(fp=path)
    edit_model_paths(thread_name=entry["thread_name"], filepath= minecraft_pack_path + "models/item/" + attachment.filename)


async def download_animation(message: discord.Message):
    attachment = message.attachments[0]  # type: ignore
    path = Path(
        minecraft_pack_path + "textures/item/" + attachment.filename
    )
    update_thread_content(message.channel.id, animation=attachment.filename)
    await attachment.save(fp=path)


def get_entry(threadid: int) -> dict | None:
    """Returns the saved entry for a given thread id

    Args:
        threadid (int): The id of the thread

    Returns:
        dict[str, str] | None: Dict of keys and saved values
        "thread_name":,
        "textures":,
        "model":,
        "owner":,
        "threshold":,
        "mcitem":,
        "isPainting":,
        "animation":,
        "message_id",
        "isDeleted"
    """
    with open(thread_content_path, "r") as file:
        data = json.load(file)

        for thread in data["threads"]:
            if list(thread.keys())[0] == str(threadid):
                return list(thread.values())[0]

        return None


def update_thread_content(threadid: int, **kwargs):
    texture = kwargs.get("texture", None)
    model = kwargs.get("model", None)
    owner = kwargs.get("owner", None)
    threshold = kwargs.get("threshold", None)
    mcitem = kwargs.get("mcitem", None)
    isPainting = kwargs.get("isPainting", None)
    animation = kwargs.get("animation", None)
    thread_name = kwargs.get("thread_name", None)
    message_id = kwargs.get("message_id", None)
    isDeleted = kwargs.get("isDeleted", None)

    contents = {
        "thread_name": thread_name,
        "textures": texture,
        "model": model,
        "owner": owner,
        "threshold": threshold,
        "mcitem": mcitem,
        "isPainting": isPainting,
        "animation": animation,
        "message_id": message_id,
        "isDeleted": isDeleted
    }

    entry = get_entry(threadid)
    if entry:  # edit
        for key, val in contents.items():
            if val and not entry[key] and key != "textures":
                entry[key] = val
            elif key == "textures":
                if val not in entry["textures"] and val:
                    entry["textures"].append(val)
    else:  # new
        contents["textures"] = [texture]
        entry = contents

    with open(thread_content_path, "r") as f:
        data = json.load(f)

        for thread in data["threads"]:
            if list(thread.keys())[0] == str(threadid):
                old_entry = list(thread.values())[0]
        try:
            data["threads"].remove({str(threadid): old_entry})  # type: ignore
        except ValueError:
            pass
        except UnboundLocalError:
            pass

    data["threads"].append({threadid: entry})

    with open(thread_content_path, "w") as f:
        json_str = json.dumps(data, indent=4)
        f.write(json_str)


def verify_uploads(threadid: int) -> bool | list | None:
    entry = get_entry(threadid=threadid)
    if not entry:
        return

    bools = {}

    for key, val in entry.items():
        if key == "textures":
            if len(val) != 0:
                bools[key] = True
            else:
                bools[key] = False
        elif key in ["threshold", "animation", "thread_name", "message_id", "isDeleted"]:
            continue

        elif key == "isPainting":
            bools["model"] = True

        else:
            if val:
                bools[key] = True
            else:
                bools[key] = False

    if all(list(bools.values())):
        return True
    else:
        false_list = []
        for key, val in bools.items():
            if not val:
                false_list.append(key)
        return false_list


def create_texture(threadid: int):
    items_path = minecraft_pack_path + "items/"
    model_path =  minecraft_pack_path + "models/item/"
    entry = get_entry(threadid=threadid)
    if not entry:
        return

    isPainting = entry["isPainting"]
    mcitem = entry["mcitem"]
    modelname = entry["model"].removesuffix(".json")

    if isPainting:
        create_painting_model(model_path, modelname)
        mcitem = "paper"  # just to make sure

    if check_item(items_path, mcitem):
        threshold = add_model_to_existing_item(items_path, mcitem, modelname)
    else:
        threshold = add_model_to_new_item(items_path, mcitem, modelname)

    update_thread_content(threadid=threadid, threshold=threshold)

    return threshold


def handle_model_name(modelname: str):
    pattern = r"[a-z0-9/._-]"
    accepted_modellist = re.findall(pattern, modelname)
    accepted_modelname = "".join(accepted_modellist)
    if accepted_modelname == modelname:
        return True
    else:
        return False


def check_recent_useruploads(author_id):
    weeknumber = datetime.datetime.now().isocalendar().week
    week_counter = 0
    if os.path.exists(thread_owners_path):
        with open(thread_owners_path, "r") as f:
            thread_owners: dict = json.load(f)
        for value in list(thread_owners.values()):
            if value["author"] == author_id and value["date"] == weeknumber:
                week_counter += 1
    return week_counter


def isAllowedToUpload(interaction: discord.Interaction, max_upload_count):
    ethisplus_id = 1497124658061770802
    assert isinstance(interaction.user, discord.Member)
    role_ids = [role.id for role in interaction.user.roles]
    upload_count = check_recent_useruploads(interaction.user.id)

    if ethisplus_id in role_ids:
        return True

    if upload_count >= max_upload_count:
        return False

    else:
        return True
