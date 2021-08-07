from bs4 import BeautifulSoup
import json
import glob
import urllib.parse

import pandas as pd
import numpy as np
import os
import requests

import requests
import shutil

import re

from PIL import Image

from bs4 import BeautifulSoup

#######

with open("data/itaiji_tobun.json") as f:
    dd = json.load(f)


def itaiji(data):
    for key in dd:
        for v in dd[key]:
            data = data.replace(v, key)

    return data

#######

import datetime
today = datetime.datetime.now()

path = "../viewer/static/t.xml"
soup = BeautifulSoup(open(path,'r'), "xml")

surfaces = soup.find_all("surface")

canvases = {}

for s in surfaces:
    zone = s.find("zone")
    canvases[zone.get("xml:id")] = s.get("source")

manifest = soup.find("facsimile").get("source")

df = requests.get(manifest).json()
images = {}
for canvas in df["sequences"][0]["canvases"]:
    images[canvas["@id"]] = canvas["thumbnail"]["@id"]

abs = soup.find(type="original").find_all("ab")

items = []

for ab in abs:
    print("---------")
    print("***", ab.previous_element.previous_element)
    print(ab)

    pb = ab.previous_element.previous_element

    if not pb:
        continue

    print("...", pb)

    try:

        texts = []

        id = pb.get("corresp").replace("#", "")

        canvas = canvases[id]

        label = id.split("_")[1] + " コマ目"

        item = {
            "objectID" : id,
            "label" : label,
            "バージョン": ["映雪草堂本"],
            "_updated": format(today, '%Y-%m-%d'),
            "manifest" : manifest,
            "member" : canvas,
            "thumbnail" : images[canvas]
        }

        for seg in ab.find_all("seg"):
            texts.append(seg.text.strip())

        item["text"] = texts

        with open("../engishiki/static/data/item/{}.json".format(item["objectID"]), 'w') as outfile:
            json.dump(item,  outfile, ensure_ascii=False,
                indent=4, sort_keys=True, separators=(',', ': '))

        fulltext = ""

        for text in texts:
            fulltext += text

        item["fulltext"] = itaiji(fulltext)
        
        items.append(item)

    except Exception as e:
        print(e)

with open("../engishiki/static/data/index.json", 'w') as outfile:
    json.dump(items,  outfile, ensure_ascii=False,
        indent=4, sort_keys=True, separators=(',', ': '))