import os
import requests
import regex as re

resourcepack = "testresource"

resourcepackfolder = r"C:\Users\Julian\AppData\Roaming\PrismLauncher\instances\Ethis for Pros 1.21.10\minecraft\resourcepacks" + "\\" + resourcepack

class Resourcepack:
    def __init__(self, name, version):
        """
        Initialize the Resourcepack class
        @param paths: list[str] Textures, Models, Items
        """
        self.name: str = name
        self.version: str = version
        self.pack_format = self.get_pack_format()[version]
        self.textures: dict = {}
        self.models: dict = {}
        self.items: list = []
        self.paths: list[str] = [f"{self.name}\\assets\\minecraft\\textures", f"{self.name}\\assets\\minecraft\\models", f"{self.name}\\assets\\minecraft\\items"]
        self.add_pack(Resourcepack.get_structure({}, resourcepackfolder))

    def add_pack(self, data_struct: dict):
        try:
            mc = data_struct["assets"]["minecraft"]

            # textures
            for cate, texture in mc.get("textures", {}).items():
                if cate not in self.textures:
                    self.textures[cate] = []
                self.textures[cate] = list(texture.keys())
            for cate, model in mc.get("models", {}).items():
                if cate not in self.models:
                    self.models[cate] = []
                self.models[cate] = list(model.keys())
            for item in mc.get("items", {}).keys():
                self.items.append(item)
        except Exception as e:
            return e

    @staticmethod
    def get_structure(struc: dict, path: str):
        # BASE CASE: empty dict → read directory
        if not struc:
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)

                if os.path.isdir(full_path):
                    struc[entry] = {}
                else:
                    struc[entry] = ""

        # RECURSE into subfolders
        for key, val in struc.items():
            if isinstance(val, dict):
                sub_path = os.path.join(path, key)
                Resourcepack.get_structure(val, sub_path)
        return struc

    def get_pack_format(self):
        response = requests.get("https://minecraft.wiki/w/Pack_format")
        raw_resourcepack = response.text.split("<caption>Resource pack formats")[1]
        format_pattern = r'pack-format">(\d+[.]*\d*)'
        version_pattern = r'Java Edition (\d\W\d+\W\d+)'
        resourcepack_formats = {}

        for line in raw_resourcepack.split("\n"):
            if '<tr id="pack-format' in line:
                formats_found = re.findall(format_pattern, line)
                versions_found = re.findall(version_pattern, line)

                if formats_found and versions_found:
                    pack_format = formats_found[0]

                    for version in versions_found:
                        resourcepack_formats[version] = pack_format
        return resourcepack_formats



    def __str__(self):
        return f"{self.name} on version {self.version} ({self.pack_format}): \nTextures: \t{self.textures}\nModels: \t{self.models}\nItems: \t{self.items}\n"

if __name__ == "__main__":
    pack = Resourcepack("pack1", "1.21.10")
    print(pack)

