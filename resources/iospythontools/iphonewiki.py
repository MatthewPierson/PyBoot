import json
import os
import urllib
from urllib.request import urlopen
import ssl
import re
import fnmatch

from bs4 import BeautifulSoup

from resources.iospythontools.ipswapi import APIParser
from resources.iospythontools.manifest import Manifest


"""
Handles data on the iphonewiki page.

Grabs keys and baseband version.
"""

def cutKeys(KeyString) -> str:
        # make it simpler to cut key string
        keys = KeyString
        if str(KeyString).startswith("=  "):
                keys = KeyString[3:]
        elif str(KeyString).startswith("= "):
            keys = KeyString[2:]
        if str(KeyString).startswith(" "):
            keys = KeyString[1:] 
        return keys

class iPhoneWiki(object):
    def __init__(self, device, version):
        super().__init__()
        self.device = device
        self.version = version

    def getWikiKeys(self):  # TODO Add OTA compatibility
        ssl._create_default_https_context = ssl._create_unverified_context
        context = ssl._create_unverified_context()
        oof = APIParser(self.device, self.version)
        buildid = oof.iOSToBuildid()
        lol = Manifest(self.device, self.version)
        codename = lol.getCodename()
        wikiUrl = f'https://www.theiphonewiki.com/w/index.php?title={codename}_{buildid}_({self.device})&action=edit'
        request = urlopen(wikiUrl, context=context).read().decode('utf-8')
        f = urlopen(wikiUrl)
        s = f.read()
        s = str(s.decode())
        #print(s)
        keysDict = {}

        if " | RootFSKey             = Not Encrypted" in s or " | RootFSKey           = Not Encrypted" in s or " | RootFSKey            = Not Encrypted" in s: # First string checks for 11.x and second for rest. For some reason its needed even though they seem the same
            print("Found Keys!")
        else: 
            keysDict['failed'] = "failed"
            return keysDict
        data = request.split('{{keys')[1].split('}}')[0].replace('|', '').splitlines()
        del data[0:8]  # Remove the top info we don't need

        ramdiskname = str(data[6])
        ramdiskname = ramdiskname[24:] + ".dmg"
        keysDict["RESTORERAMDISK"] = ramdiskname
        if " | Model2                =" in s:
            multiplekeys = True
            print("Found a keys page with multiple models...\nWhich is your device?")
            for keys in data:
                if r"  Model " in keys:
                    keys = keys[24:]
                    keys = cutKeys(keys) 
                    print(f"1: {keys}")
                    model1 = keys
                if r"  Model2 " in keys:
                    keys = keys[24:]
                    keys = cutKeys(keys) 
                    print(f"2: {keys}")
                    model2 = keys
            modelnum = input("Enter 1 or 2: ")
            if modelnum == "1":
                print(f"User chose {model1}, grabbing those keys...")
                pass
            elif modelnum == "2":
                print(f"User chose {model2}, grabbing those keys...")
                pass
            else:
                print("User chose an invalid option, exiting...")
                exit(2)
        else:
            multiplekeys = False
        if multiplekeys:
            if modelnum == "1":
                for keys in data:
                    #We don't actually need most of these keys, but might as well store them
                    # For some reason, 11.x keys contain '= ' after cutting and 10x contains '=  ' after cutting so we need to check for that and handle it if found
                    # Need to redo this as a nice clean function =) 
                    if r"  iBEC " in keys:
                        keys = keys[24:]
                        keys = cutKeys(keys)  
                        keysDict['IBEC'] = keys
                        #print(keysDict)
                    if r"  iBECIV " in keys:
                        keys = keys[24:]
                        keys = cutKeys(keys) 
                        keysDict['IBECIV'] = keys
                        #print(keysDict)
                    if r"  iBECKey " in keys:
                        keys = keys[24:]
                        keys = cutKeys(keys) 
                        keysDict['IBECKEY'] = keys
                        #print(keysDict)
                    if r"  iBSS " in keys:
                        keys = keys[24:]
                        keys = cutKeys(keys) 
                        keysDict['IBSS'] = keys
                        #rint(keysDict)
                    if r"  iBSSIV " in keys:
                        keys = keys[24:]
                        keys = cutKeys(keys) 
                        keysDict['IBSSIV'] = keys
                        #print(keysDict)
                    if r"  iBSSKey " in keys:
                        keys = keys[24:]
                        keys = cutKeys(keys) 
                        keysDict['IBSSKEY'] = keys
                        #print(keysDict)
                    if r"  LLBIV " in keys:
                        keys = keys[23:]
                        keys = cutKeys(keys) 
                        keysDict['LLBIV'] = keys
                        #print(keysDict)
                    if r"  LLBKey " in keys:
                        keys = keys[24:]
                        keys = cutKeys(keys) 
                        keysDict['LLBKEY'] = keys
                        #print(keysDict)
                    if r"  iBootIV " in keys:
                        keys = keys[25:]
                        keys = cutKeys(keys) 
                        keysDict['IBOOTIV'] = keys
                        #print(keysDict)
                    if r"  iBootKey " in keys:
                        keys = keys[26:]
                        keys = cutKeys(keys) 
                        keysDict['IBOOTKEY'] = keys
                        #print(keysDict)
                return keysDict
            elif modelnum == "2":
                for keys in data:
                    #We don't actually need most of these keys, but might as well store them
                    # For some reason, 11.x keys contain '= ' after cutting and 10x contains '=  ' after cutting so we need to check for that and handle it if found
                    # Need to redo this as a nice clean function =) 
                    if r"  iBEC2 " in keys:
                        keys = keys[24:]
                        keys = cutKeys(keys)  
                        keysDict['IBEC'] = keys
                        #print(keysDict)
                    if r"  iBEC2IV " in keys:
                        keys = keys[24:]
                        keys = cutKeys(keys) 
                        keysDict['IBECIV'] = keys
                        #print(keysDict)
                    if r"  iBEC2Key " in keys:
                        keys = keys[24:]
                        keys = cutKeys(keys) 
                        keysDict['IBECKEY'] = keys
                        #print(keysDict)
                    if r"  iBSS2 " in keys:
                        keys = keys[24:]
                        keys = cutKeys(keys) 
                        keysDict['IBSS'] = keys
                        #rint(keysDict)
                    if r"  iBSS2IV " in keys:
                        keys = keys[24:]
                        keys = cutKeys(keys) 
                        keysDict['IBSSIV'] = keys
                        #print(keysDict)
                    if r"  iBSS2Key " in keys:
                        keys = keys[24:]
                        keys = cutKeys(keys) 
                        keysDict['IBSSKEY'] = keys
                        #print(keysDict)
                    if r"  LLB2IV " in keys:
                        keys = keys[23:]
                        keys = cutKeys(keys) 
                        keysDict['LLBIV'] = keys
                        #print(keysDict)
                    if r"  LLB2Key " in keys:
                        keys = keys[24:]
                        keys = cutKeys(keys) 
                        keysDict['LLBKEY'] = keys
                        #print(keysDict)
                    if r"  iBoot2IV " in keys:
                        keys = keys[25:]
                        keys = cutKeys(keys) 
                        keysDict['IBOOTIV'] = keys
                        #print(keysDict)
                    if r"  iBoot2Key " in keys:
                        keys = keys[26:]
                        keys = cutKeys(keys) 
                        keysDict['IBOOTKEY'] = keys
                        #print(keysDict)
                return keysDict
        else:
            for keys in data:
                #We don't actually need most of these keys, but might as well store them
                # For some reason, 11.x keys contain '= ' after cutting and 10x contains '=  ' after cutting so we need to check for that and handle it if found
                # Need to redo this as a nice clean function =) 
                if r"  iBEC " in keys:
                    keys = keys[24:]
                    keys = cutKeys(keys)  
                    keysDict['IBEC'] = keys
                    #print(keysDict)
                if r"  iBECIV " in keys:
                    keys = keys[24:]
                    keys = cutKeys(keys) 
                    keysDict['IBECIV'] = keys
                    #print(keysDict)
                if r"  iBECKey " in keys:
                    keys = keys[24:]
                    keys = cutKeys(keys) 
                    keysDict['IBECKEY'] = keys
                    #print(keysDict)
                if r"  iBSS " in keys:
                    keys = keys[24:]
                    keys = cutKeys(keys) 
                    keysDict['IBSS'] = keys
                    #rint(keysDict)
                if r"  iBSSIV " in keys:
                    keys = keys[24:]
                    keys = cutKeys(keys) 
                    keysDict['IBSSIV'] = keys
                    #print(keysDict)
                if r"  iBSSKey " in keys:
                    keys = keys[24:]
                    keys = cutKeys(keys) 
                    keysDict['IBSSKEY'] = keys
                    #print(keysDict)
                if r"  LLBIV " in keys:
                    keys = keys[23:]
                    keys = cutKeys(keys) 
                    keysDict['LLBIV'] = keys
                    #print(keysDict)
                if r"  LLBKey " in keys:
                    keys = keys[24:]
                    keys = cutKeys(keys) 
                    keysDict['LLBKEY'] = keys
                    #print(keysDict)
                if r"  iBootIV " in keys:
                    keys = keys[25:]
                    keys = cutKeys(keys) 
                    keysDict['IBOOTIV'] = keys
                    #print(keysDict)
                if r"  iBootKey " in keys:
                    keys = keys[26:]
                    keys = cutKeys(keys) 
                    keysDict['IBOOTKEY'] = keys
                    #print(keysDict)
            return keysDict
                
