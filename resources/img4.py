import os
import subprocess
import sys
import re
import shutil
import time
from resources.iospythontools import iphonewiki, ipswapi
from pyboot import *
from subprocess import check_output
try:

    from PIL import Image

except:
    print("Failed to import dependencies, please run 'pip3 install -r requirements.txt' then re-run PyBoot")
    exit(2)

def signImages():
    print("Signing boot files")
    # time to sign shit
    so = subprocess.Popen(f"./resources/bin/img4tool -c resources/devicetree.img4 -p resources/devicetree.im4p -s resources/shsh.shsh", stdout=subprocess.PIPE, shell=True)
    output = so.stdout.read()

    so = subprocess.Popen(f"./resources/bin/img4toolkernel -c resources/kernel.img4 -p resources/kernel.im4p -s resources/shsh.shsh", stdout=subprocess.PIPE, shell=True)
    output = so.stdout.read()

    so = subprocess.Popen(f"./resources/bin/img4tool -c resources/trustcache.img4 -p resources/trustcache.im4p -s resources/shsh.shsh", stdout=subprocess.PIPE, shell=True)
    output = so.stdout.read()
def patchFiles(iOSVersion):
    if os.path.isfile("resources/kernel.im4p"): 
        print("Patching Kernel's type from krnl to rkrn")
        with open("resources/kernel.im4p", "r+b") as fh:
            file = fh.read()
            try:
                offset = hex(file.index(b"\x6b\x72\x6e\x6c")) # getting offset for tag krnl tag, can be 1 or 2 bytes off depending on the kernel
                offset = int(offset, 16)
                fh.seek(offset, 0)
                fh.write(b"\x72\x6b\x72\x6e") # writing rkrn tag so we can boot =)
                fh.close()
            except:
                print("Kernel patching failed!")
                exit(2)
    if "11." in iOSVersion:
        print("iOS version is 11.x, skipping trustcache patching")
        pass
    elif "10." in iOSVersion:
        print("iOS version is 10.x, skipping trustcache patching")
        pass
    else:
        if os.path.exists("resources/trustcache.im4p"):
            print("Patching TrustCache's type from trst to rtsc")
            with open("resources/trustcache.im4p", "r+b") as fh:
                file = fh.read()
                try:
                    offset = hex(file.index(b"\x74\x72\x73\x74")) # getting offset for tag trst tag, can be 1 or 2 bytes off depending on the trustcache
                    offset = int(offset, 16)
                    fh.seek(offset, 0)
                    fh.write(b'\x72\x74\x73\x63') # writing rtsc tag so we can boot =)
                    fh.close()
                except:
                    print("Trustcache patching failed!")
                    exit(2)
        else:
            print("Error: Couldn't find resources/trustcache.im4p, patching failed")
            exit(2)
    if os.path.exists("resources/devicetree.im4p"):
        print("Patching Devicetree's type from dtre to rdtr")
        with open("resources/devicetree.im4p", "r+b") as fh:
            file = fh.read()
            try:
                offset = hex(file.index(b"\x64\x74\x72\x65")) # getting offset for tag dtre tag, can be 1 or 2 bytes off depending on the devicetree
                offset = int(offset, 16)
                fh.seek(offset, 0)
                fh.write(b'\x72\x64\x74\x72')  # writing rdtr tag so we can boot =)
                fh.close()
            except:
                print("Devicetree patching failed!")
                exit(2)
def downloadImages(ipswURL, filepath, savepath):
    try:

        cmd = f"./resources/bin/pzb download {ipswURL} {filepath} {savepath}"
        so = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        download = so.stdout.read()
        return
    except:
        print(f"Failed to download {filepath} from {ipswURL}. Most likely access denied from Apple")
        exit(2)
def sendImages(iosVersion, useCustomLogo):
    print("Sending boot files to the device and booting")
    os.chdir("resources")
    time.sleep(3)

    cmd = "bin/irecovery -f ibss.img4"
    so = subprocess.Popen(cmd, shell=True)
    time.sleep(2)

    cmd = "bin/irecovery -f ibec.img4"
    so = subprocess.Popen(cmd, shell=True)
    time.sleep(2)

    cmd = 'bin/irecovery -c "bootx"' # Testing if running bootx after ibss/ibec will fix devicetree issues
    so = subprocess.Popen(cmd, shell=True)

    if useCustomLogo:
        cmd = f"bin/irecovery -f bootlogo.img4"
        so = subprocess.Popen(cmd, shell=True)
        
        cmd = 'bin/irecovery -c "setpicture 0"'
        so = subprocess.Popen(cmd, shell=True)

        cmd = 'bin/irecovery -c "bgcolor 0 0 0"'
        so = subprocess.Popen(cmd, shell=True)

    cmd = "bin/irecovery -f devicetree.img4"
    so = subprocess.Popen(cmd, shell=True)
    time.sleep(2)

    cmd = 'bin/irecovery -c "devicetree"'
    so = subprocess.Popen(cmd, shell=True)
    print(so) # For some weird reason, devicetree won't execute properly unless I print this?????? If I don't then I have to send devicetree/trustcache/kernel again after bootx fails
    time.sleep(2)

    if not '11.' in iosVersion: # 11.x and lower don't need trustcache sent to boot =)

        cmd = "bin/irecovery -f trustcache.img4"
        so = subprocess.Popen(cmd, shell=True)
        time.sleep(2)

        cmd = 'bin/irecovery -c "firmware"'
        so = subprocess.Popen(cmd, shell=True)
        time.sleep(2)

    cmd = "bin/irecovery -f kernel.img4"
    so = subprocess.Popen(cmd, shell=True)
    time.sleep(2)

    cmd = 'bin/irecovery -c "bootx"'
    so = subprocess.Popen(cmd, shell=True)
    time.sleep(2)

    print("Should be good?")
    os.chdir("../")
def img4stuff(deviceModel, iOSVersion, useCustomLogo, bootlogoPath):
    bootchainVariants = { # iBoot64Patcher doesn't work for iOS 13 iBSS/iBEC so we have to get 12.x iBSS/iBEC to use for booting, but still grab kernel/trustcache (If needed)/devicetree for downgraded iOS version
    'iPhone8,1': '12.4',
    'iPhone8,2': '13.1.3', # This device has NO keys for 11.x/12.x but i'll keep it here for when it does
    'iPhone9,1': '12.4',
    'iPhone9,2': '12.3.1',
    'iPhone9,3': '12.3.1',
    'iPhone9,4': '12.3.1',
    'iPhone10,3': '12.3.1',
    'iPhone10,6': '12.4',
    'iPod7,1': '12.3.1',
    'iPad7,5': '12.3.1',
    'iPad7,6': '12.3.1',
    'iPhone6,2': iOSVersion, # Since these have all keys up, we can just use whatever the downgraded version is =)
    'iPhone6,1': iOSVersion,
    'iPhone7,2': iOSVersion,
    'iPhone7,1': iOSVersion # This device has NO keys for 11.x/12.x but i'll keep it here for when it does
    }
    screenSize = {
    'iPhone8,1': '1334x750',
    'iPhone8,2': '1920x1080',
    'iPhone9,1': '1334x750',
    'iPhone9,2': '1920x1080',
    'iPhone9,3': '1334x750',
    'iPhone9,4': '1920x1080',
    'iPhone10,3': '2436x1125',
    'iPhone10,6': '2436x1125',
    'iPhone6,2': '1136x640',
    'iPhone6,1': '1136x640',
    'iPhone7,2': '1334x750',
    'iPhone7,1': '1920x1080',
    }
    try:
        iosBootChainVersion = bootchainVariants[deviceModel] # Have to use a 12.x iBSS/iBEC for now since iBoot64Patcher can't patch 13.x stuff yet
    except:
        print("Sorry your device has no 12.x or lower keys meaning tether booting isn't possible\nThat or I forgot to add your device to the list, please let me know if thats the case!")
        exit(2)
    print(f"Checking theiphonewiki for {iosBootChainVersion} keys...")
    wiki = iphonewiki.iPhoneWiki(deviceModel, iosBootChainVersion)
    keys = wiki.getWikiKeys() 

    iBECName = keys["IBEC"]
    iBECKey = keys["IBECKEY"]
    iBECIV = keys["IBECIV"]

    iBSSName = keys["IBSS"]
    iBSSKey = keys["IBSSKEY"]
    iBSSIV = keys["IBSSIV"]
    if iBECIV == "Unknown": # Just making sure that there is keys, some key pages have keys for one model but not the other which could cause issues
        print("Keys for the other device model are present but not for yours sorry\nFeel free to get them and add them to theiphonewiki =)")
        exit(2)
    so = subprocess.Popen(f"/usr/bin/curl https://api.ipsw.me/v2.1/{deviceModel}/{iOSVersion}/url", stdout=subprocess.PIPE, shell=True)
    output = so.stdout.read()
    ipswurl = str(output)[2:-1] # Have to cut b' from the start and ' from the end of the string

    so = subprocess.Popen(f"/usr/bin/curl https://api.ipsw.me/v2.1/{deviceModel}/{iosBootChainVersion}/url", stdout=subprocess.PIPE, shell=True)
    output = so.stdout.read()
    iburl = str(output)[2:-1] # Have to cut b' from the start and ' from the end of the string
     #geting shsh
    print("Getting SHSH for signing images")
    so = subprocess.Popen(f"./resources/bin/tsschecker -d iPhone6,2 -e 12326262 -l -s", stdout=subprocess.PIPE, shell=True)
    getshsh = so.stdout.read()
    dir_name = os.getcwd()
    test = os.listdir(dir_name)
    for item in test:
        if item.endswith(".shsh2"):
            shutil.move(os.path.join(dir_name, item), "./resources/shsh.shsh")
    shsh = "./resources/shsh.shsh"
    if os.path.exists(shsh):
        # Always good to check it saved properly
        pass
    else:
        sys.exit("ERROR: Failed to save shsh")
    print(f"Downloading and patching {iosBootChainVersion}'s iBSS/iBEC")
    #pzb to get ibss and ibec
    downloadImages(iburl, f"Firmware/dfu/{iBECName}", "resources/ibec.im4p")

    downloadImages(iburl, f"Firmware/dfu/{iBSSName}", "resources/ibss.im4p")

    # Assuming that worked (add checks) we now need to decrpyt and patch iBSS/iBEC for booting
    so = subprocess.Popen(f"./resources/bin/img4tool -e -o resources/ibss.raw --iv {iBSSIV} --key {iBSSKey} resources/ibss.im4p", stdout=subprocess.PIPE, shell=True)
    output = so.stdout.read()
    if useCustomLogo:
        so = subprocess.Popen(f'./resources/bin/iBoot64Patcher resources/ibss.raw resources/ibss.pwn', stdout=subprocess.PIPE, shell=True)
        output = so.stdout.read()
    else:
        so = subprocess.Popen(f'./resources/bin/iBoot64Patcher resources/ibss.raw resources/ibss.pwn -b "-v"', stdout=subprocess.PIPE, shell=True)
        output = so.stdout.read()

    so = subprocess.Popen(f"./resources/bin/img4tool -e -o resources/ibec.raw --iv {iBECIV} --key {iBECKey} resources/ibec.im4p", stdout=subprocess.PIPE, shell=True)
    output = so.stdout.read()
    if useCustomLogo:
        so = subprocess.Popen(f'./resources/bin/iBoot64Patcher resources/ibec.raw resources/ibec.pwn', stdout=subprocess.PIPE, shell=True)
        output = so.stdout.read()
    else:
        so = subprocess.Popen(f'./resources/bin/iBoot64Patcher resources/ibec.raw resources/ibec.pwn -b "-v"', stdout=subprocess.PIPE, shell=True)
        output = so.stdout.read()

    so = subprocess.Popen(f"./resources/bin/img4tool -c resources/ibec.patched -t ibec resources/ibec.pwn", stdout=subprocess.PIPE, shell=True)
    output = so.stdout.read()

    so = subprocess.Popen(f"./resources/bin/img4tool -c resources/ibss.patched -t ibss resources/ibss.pwn", stdout=subprocess.PIPE, shell=True)
    output = so.stdout.read()

    so = subprocess.Popen(f"./resources/bin/img4tool -c resources/ibss.img4 -p resources/ibss.patched -s resources/shsh.shsh", stdout=subprocess.PIPE, shell=True)
    output = so.stdout.read()

    so = subprocess.Popen(f"./resources/bin/img4tool -c resources/ibec.img4 -p resources/ibec.patched -s resources/shsh.shsh", stdout=subprocess.PIPE, shell=True)
    output = so.stdout.read()
        
    if useCustomLogo:
        # Now need to convert the .PNG to a img4 format to use while booting
        # check png dimensions, make sure its the proper size even though we won't stop if its not
        im = Image.open(bootlogoPath)
        w, h = im.size
        check = f"{h}x{w}"
        if screenSize[deviceModel] == check:
            print("Image is correct size and format")
        else:
            print(f"Image is {check} but screen is {screenSize[deviceModel]}.\nContinuing anyway, although image may look strange on the device")
        # Now run ibootim 
        if str(bootlogoPath).lower().endswith(".png"):
            so = subprocess.Popen(f"./resources/bin/ibootim {bootlogoPath} resources/bootlogo.ibootim", stdout=subprocess.PIPE, shell=True) # Thanks to realnp for ibootim!
            output = so.stdout.read()
            # now create im4p
            so = subprocess.Popen(f"./resources/bin/img4tool -c resources/bootlogo.im4p -t logo resources/bootlogo.ibootim", stdout=subprocess.PIPE, shell=True)
            output = so.stdout.read()
            # Add signature from shsh 
            so = subprocess.Popen(f"./resources/bin/img4tool -c resources/bootlogo.img4 -p resources/bootlogo.im4p -s resources/shsh.shsh", stdout=subprocess.PIPE, shell=True)
            output = so.stdout.read()
            bootlogoPath = "resources/bootlogo.img4"
        else:
            print("Please provide a .png file, other image types are not supported")
            exit(2)
    else:
        pass
    # iBSS/iBEC stuff is done, we now need to get devicetree, trustcache and kernel
    print(f"Downloading {iOSVersion}'s BuildManifest.plist")
    try:
        downloadImages(ipswurl, "BuildManifest.plist", "resources/manifest.plist")
    except:
        print("ERROR: Failed to download BuildManifest.plist\nPlease re-run PyBoot again and it should work (might take a few tries)")
        exit(2)
    line_number = 0
    with open("./resources/manifest.plist", mode="rt") as read_plist:
        for line in read_plist:
            line_number += 1
            if re.search("kernelcache.release.+", line):
                kernelname = line.rstrip()
                read_plist.close()
                break
    kernelname = kernelname[14:-9]  
    print(f"Downloading {iOSVersion}'s KernelCache")  
    try:
        downloadImages(ipswurl, kernelname, "resources/kernel.im4p")
    except:
        print("ERROR: Failed to download Kernel\nPlease re-run PyBoot again and it should work (might take a few tries)")
        exit(2)
    devicetreename = f"DeviceTree.{iBSSName[5:-13]}ap.im4p"
    if deviceModel == "iPhone6,2":
        devicetreename = "DeviceTree.n53ap.im4p"
    elif deviceModel == "iPhone6,1":
        devicetreename = "DeviceTree.n51ap.im4p"
    print(f"Downloading {iOSVersion}'s DeviceTree")
    try:
        downloadImages(ipswurl, f"Firmware/all_flash/{devicetreename}", "resources/devicetree.im4p")
    except:
        print("ERROR: Failed to download DeviceTree\nPlease re-run PyBoot again and it should work (might take a few tries)")
        exit(2)
    so = check_output(f"./resources/bin/pzb list {ipswurl}", shell=True) # Need to check the downgraded IPSW to get the rootfs trustcache for booting
    so = str(so)
    rootfsoffset = so.find("GB") - 24 # This should always work, unless for some reason another file in the IPSW is > 1GB
    rootfsName = so[int(rootfsoffset):-51] # This should be the correct number to cut from, will test more

    if '11.' in iOSVersion:
        print("iOS version is 11.x, not downloading trustcache")
        pass
    elif '10.' in iOSVersion:
        print("iOS version is 10.x, not downloading trustcache")
        pass
    else:
        if rootfsName.endswith(".dmg"):
            # just making sure string was cut correctly
            keys["ROOTFSNAME"] = rootfsName
            print(f"Downloading {iOSVersion}'s TrustCache")
            try:
                downloadImages(ipswurl, f'Firmware/{rootfsName}.trustcache', "resources/trustcache.im4p")
            except:
                print("ERROR: Failed to download TrustCache\nPlease re-run PyBoot again and it should work (might take a few tries)")
                exit(2)
            time.sleep(5)
        else:
            print("Failed to get RootFS name\nPlease read through this output and enter the name of the largest .dmg file\n")
            rootfsName = input()
            if rootfsName.endswith(".dmg"):
                # checking again and exiting if you enter wrong because you suck
                keys["ROOTFSNAME"] = rootfsName
                downloadImages(ipswurl, f'Firmware/{rootfsName}.trustcache', "resources/trustcache.im4p")
                time.sleep(5)
            else:
                print("Start again from the beggining =)")
                exit(2)
    # Can add a verification for after the patching to make sure it was applied correctly and in the right place just in case
    patchFiles(iOSVersion)
    print("Signing boot files")
    signImages()
