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

def getManifest(uri):
    df = requests.get(uri).json()
    canvases = df["sequences"][0]["canvases"]
    map = {}
    for i in range(len(canvases)):
        cid = canvases[i]["@id"]
        map[i + 1] = cid
    return map





df_multi = pd.read_excel("水滸伝.xlsx", sheet_name=[0, 1], header=None, index_col=None, engine='openpyxl')

df = df_multi[0]


r_count = len(df.index)
c_count = len(df.columns)


prev_page = ""
prev_num = 1000

ab = ""

file = "template.xml"

soup = BeautifulSoup(open(file,'r'), "xml")

vol = 1

original = soup.find_all("div")[0]

key = "a"

########

def getNotes(df):
    r_count = len(df.index)
    c_count = len(df.columns)

    ab = soup.find_all("div")[1].find("ab")

    zones = {}

    for i in range(1, r_count):
        type = df.iloc[i, 2]
        subtype = df.iloc[i, 3]

        text = df.iloc[i, 6]
        page = df.iloc[i, 7]
        id = df.iloc[i, 8]
        image = df.iloc[i, 9]

        if pd.isnull(text):
            continue

        note = soup.new_tag("note")
        text = text.replace("/", "<lb/>")
        note.append(BeautifulSoup("<p>{}</p>".format(text), 'xml'))

        note["corresp"] = "#zone_" + id
        note["target"] = id
        note["type"] = type
        note["subtype"] = subtype

        ab.append(note)

        #####

        if page not in zones:
            zones[page] = []

        xywh = image.split("/")[-4].split(",")

        x = int(xywh[0])
        y = int(xywh[1])
        w = int(xywh[2])
        h = int(xywh[3])

        zone = soup.new_tag("zone")
        zone["xml:id"] = "zone_"+id
        zone["ulx"] = x
        zone["uly"] = y
        zone["lrx"] = x + w
        zone["lry"] = y + h

        zones[page].append(zone)

    return zones

zones = getNotes(df_multi[1])

########

uri = "https://suikoden.netlify.app/manifest.json"

manifests = getManifest(uri)

facsimile = soup.find("facsimile")
facsimile["source"] = uri

for index in manifests:
    surface = soup.new_tag("surface")
    facsimile.append(surface)
    surface["source"] = manifests[index]

    zone = soup.new_tag("zone")
    surface.append(zone)
    zone["xml:id"] = "zone_{}".format(index)

    key2 = "01-{}".format(str(index).zfill(4))

    if key2 in zones:
        for z in zones[key2]:
            surface.append(z)

########



for i in range(1, r_count):
    page = df.iloc[i, 0]

    text = df.iloc[i, 2]

    if pd.isnull(text):
        continue

    #####

    initFlag = False

    if pd.isnull(page):
        page = prev_page
    else:
        prev_page = page
        initFlag = True

    num = int(df.iloc[i, 1])

    

    # page切り替え
    if initFlag:
        pb = soup.new_tag("pb")
        original.append(pb)

        index = int(page.split("-")[1])
        pb["corresp"] = "#zone_{}".format(index)
    
    if prev_num > num:

        ab = soup.new_tag("ab")
        original.append(ab)
        # ab.append("ccc")

        key = "b" if key == "a" else "a"

    
    prev_num = num

    #####

    



    lb = soup.new_tag("lb")
    ab.append(lb)
    lb["xml:id"] = "l{}-{}-{}-{}".format(str(vol).zfill(2), str(page).zfill(4), key, num)

    #####

    text = re.sub(r"<(.+?)>", "<space n=\"{}\"/>".format("\\1"), text)

    text = re.sub(r"\[(.+?)\]", "<anchor xml:id=\"{}\"/>".format("\\1"), text)

    ab.append(BeautifulSoup("<seg>{}</seg>".format(text), 'xml'))

    '''
    if i > 30:
        break
    '''

html = soup.prettify("utf-8")
with open("/Users/nakamurasatoru/git/d_nagai/viewer/static/t.xml", "wb") as file:
    file.write(html)
