import os
import json

def get_current_items_in_folder(folderpath: str):
    items = [entry for entry in os.listdir(folderpath)]
    print(items)

def get_content_of_file(filepath: str) -> dict | None:
    if not os.path.isfile(filepath):
        return None
    with open(filepath) as f:
        content_str = f.read()
        return json.loads(content_str)


def add_model_to_existing_item(new_item: str, exist_item: str):
    pass


path = r"C:\Users\Julian\AppData\Roaming\PrismLauncher\instances\Ethis for Pros 1.21.10\minecraft\resourcepacks\testresource\assets\minecraft\items"
get_current_items_in_folder(path)
jsonobject = (get_content_of_file(path + "\\" + "carved_pumpkin.json"))
print(jsonobject)
