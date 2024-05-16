import os, shutil

def first(selecteditem):
    data = {
    "parent": "minecraft:item/handheld",
    "textures": {
      "layer0": "minecraft:item/" + selecteditem
    }
  }
    return data

def move(itemname, foldername):
    shutil.move(itemname, foldername)
