import os, shutil, json


def first(selecteditem):
    data = {
        "parent": "minecraft:item/handheld",
        "textures": {"layer0": "minecraft:item/" + selecteditem},
    }
    return data


def move_texture(itemname, foldername):
    print("test:", itemname)
    destination = foldername + "/assets/minecraft/textures/item"
    shutil.move(itemname, destination)
    print("moved " + itemname + " to " + destination)


def create_model(itemname, foldername):
    name = itemname.split("/")[-1].split(".")[0]
    json1 = json.dumps(first(name), indent=4)

    # Writing to sample.json
    destination = foldername + "/assets/minecraft/models/item"
    with open(f"{destination}/{name}_model.json", "w") as outfile:
        outfile.write(json1)




def edit_or_create(selecteditem, itemname, foldername):
    item = itemname.split("/")[-1].split(".")[0]
    destination = os.path.join(foldername, "assets/minecraft/models/item")
    filepath = os.path.join(destination, f"{selecteditem}.json")
    if os.path.exists(filepath):
        edit_existing_override(filepath, item)
    else:
        create_new_override(selecteditem, itemname, foldername)

def edit_existing_override(filepath, item):
    with open(filepath, "r") as file:
        data = json.load(file)
    
    # Find the highest custom_model_data value
    max_custom_model_data = 0
    if "overrides" in data:
        for override in data["overrides"]:
            if "predicate" in override and "custom_model_data" in override["predicate"]:
                max_custom_model_data = max(max_custom_model_data, override["predicate"]["custom_model_data"])
    
    # Increment the highest custom_model_data by 1
    new_custom_model_data = max_custom_model_data + 1
    
    new_override = {
        "predicate": {"custom_model_data": new_custom_model_data},
        "model": f"minecraft:item/{item}_model"
    }
    
    if "overrides" in data:
        data["overrides"].append(new_override)
    else:
        data["overrides"] = [new_override]
    
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)

def create_new_override(selecteditem, itemname, foldername):
    item = itemname.split("/")[-1].split(".")[0]
    data = {
        "parent": "minecraft:item/handheld",
        "textures": {"layer0": "minecraft:item/" + selecteditem},
        "overrides": [
            {
                "predicate": {"custom_model_data": 2},
                "model": "minecraft:item/" + item + "_model",
            }
        ],
    }
    destination = os.path.join(foldername, "assets/minecraft/models/item")
    
    # Ensure the destination directory exists
    os.makedirs(destination, exist_ok=True)
    
    filepath = os.path.join(destination, f"{selecteditem}.json")
    with open(filepath, "w") as outfile:
        json.dump(data, outfile, indent=4) 

def move_back_texture():
    item = "C:/Users/Julian/OneDrive - Quadraam/Documenten/Github/Resourcepack-editing/server resource pack/assets/minecraft/textures/item/pink_sword.png"
    destination = (
        "C:/Users/Julian/OneDrive - Quadraam/Documenten/Github/Resourcepack-editing"
    )
    shutil.move(item, destination)

def test():
  foldername = "C:/Users/Julian/OneDrive - Quadraam/Documenten/Github/Resourcepack-editing/server resource pack"
  selecteditem = "netherite_sword"
  openfile = os.path.join(foldername, "assets/minecraft/models/item/", f"{selecteditem}.json")
  # print the json file
  with open(openfile, "r") as file:
    print(file.read())

if __name__ == "__main__":
    move_back_texture()
    #test()

