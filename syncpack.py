import shutil

destination = "C:\\Users\\Julian\\AppData\\Roaming\\.minecraft\\resourcepacks"
source = "C:\\Users\\Julian\\Documents\\Github\\Resourcepack-editing\\pack"

operation = shutil.copytree(source, destination, dirs_exist_ok=True)
