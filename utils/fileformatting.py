import os
import json
from main import resourcepackfolder

def get_current_items_in_folder(folderpath: str) -> list[str]:
    items = [entry for entry in os.listdir(folderpath)]
    return items

def get_content_of_file(filepath: str) -> dict | None:
    if not os.path.isfile(filepath):
        return None
    with open(filepath) as f:
        content_str = f.read()
        return json.loads(content_str)

def check_item(path, mc_item):
    if os.path.isfile(path+f"{mc_item}.json"):
        return True
    else:
        return False

def add_model_to_existing_item(path, mc_item, model_name) -> int: # type: ignore
    content = get_content_of_file(path + f"{mc_item}.json")
    if content:        
        
        # Adding all item entries to a python list
        entries = []
        highest_treshhold = len(entries)
        for entry in content["model"]["entries"]:
            entries.append(entry)
            if entry["threshold"] >= highest_treshhold:
                highest_treshhold = entry["threshold"]
        
        # creating a new entry
        entry_format = {"threshold": highest_treshhold+1, "model": {"type": "minecraft:model", "model": f"item/{model_name}"}}
        print(str(entry_format["model"]))
        print( [str(entry_str["model"]) for entry_str in entries])
        if str(entry_format["model"]) not in [str(entry_str["model"]) for entry_str in entries]:
            entries.append(entry_format)
            highest_treshhold+=1
        
        content["model"]["entries"] = entries
        
        # Writing to json
        content_str = json.dumps(content, indent=4)
        with open(path + f"{mc_item}.json", mode="w") as f:
            f.write(content_str)
        return highest_treshhold

def add_model_to_new_item(path, mc_item, model_name) -> int: # type: ignore
    content = {
    "model": {
        "type": "minecraft:range_dispatch",
        "property": "minecraft:custom_model_data",
        "entries": [],
        "fallback": {
            "type": "minecraft:model",
            "model": f"minecraft:item/{mc_item}"
        }
        }
    }
    entries = []
    entry_format = {"threshold": 1, "model": {"type": "minecraft:model", "model": f"item/{model_name}"}}
    entries.append(entry_format)
    content["model"]["entries"] = entries

    # Writing to json
    content_str = json.dumps(content, indent=4)
    with open(path + f"{mc_item}.json", mode="w") as f:
        f.write(content_str)
    return 1

def create_painting_model(path, model_name):
    content = {
        "format_version": "1.21.11",
        "credit": "Script written by Skywalkered",
        "textures": {
            "0": f"minecraft:item/{model_name}",
            "particle": f"minecraft:item/{model_name}"
        },
        "elements": [
            {
                "from": [0, 0, 8],
                "to": [16, 16, 8],
                "rotation": {"angle": 0, "axis": "y", "origin": [0, 0, 6]},
                "faces": {
                    "north": {"uv": [0, 0, 16, 16], "texture": "#0"},
                    "south": {"uv": [0, 16, 16, 32], "texture": "#0"}
                }
            }
        ],
        "display": {
            "fixed": {
                "translation": [0, 0, -0.1],
                "scale": [2, 2, 1]
            }
        }
    }
    # Writing to json
    content_str = json.dumps(content, indent=4)
    with open(path + f"{model_name}.json", mode="w") as f:
        f.write(content_str)



def get_mc_items():
    pass

# # 1. check if mc_item already exists
# # 2.    if yes, add new model and return index
# #       if not, make a new JSON file and return index
# resourcepack_path = resourcepackfolder
# item_suffix = r"\\assets\minecraft\items\\"
# model_item_suffix = r"\\assets\minecraft\models\item\\"
# model_texture_suffix = r"\\assets\minecraft\textures\item\\"

