import os
import re
import shutil
import subprocess
import sys
import time
from subprocess import check_output

import requests

from resources.iospythontools import iphonewiki, ipswapi

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
                offset = hex(file.index(b"\x6b\x72\x6e\x6c"))  # getting offset for tag krnl tag, can be 1 or 2 bytes off depending on the kernel
                offset = int(offset, 16)
                fh.seek(offset, 0)
                fh.write(b"\x72\x6b\x72\x6e")  # writing rkrn tag so we can boot =)
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
                    offset = hex(file.index(b"\x74\x72\x73\x74"))  # getting offset for tag trst tag, can be 1 or 2 bytes off depending on the trustcache
                    offset = int(offset, 16)
                    fh.seek(offset, 0)
                    fh.write(b'\x72\x74\x73\x63')  # writing rtsc tag so we can boot =)
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
                offset = hex(file.index(b"\x64\x74\x72\x65"))  # getting offset for tag dtre tag, can be 1 or 2 bytes off depending on the devicetree
                offset = int(offset, 16)
                fh.seek(offset, 0)
                fh.write(b'\x72\x64\x74\x72')  # writing rdtr tag so we can boot =)
                fh.close()
            except:
                print("Devicetree patching failed!")
                exit(2)


def sendImages(iosVersion, useCustomLogo):
    print("Sending boot files to the device and booting")
    if os.path.exists("resources"):
        os.chdir("resources")
    else:
        pass
    time.sleep(3)

    cmd = "bin/irecovery -f ibss.img4"
    so = subprocess.Popen(cmd, shell=True)
    time.sleep(2)

    cmd = "bin/irecovery -f ibec.img4"
    so = subprocess.Popen(cmd, shell=True)
    time.sleep(2)

    cmd = 'bin/irecovery -c "bootx"'  # Testing if running bootx after ibss/ibec will fix devicetree issues
    so = subprocess.Popen(cmd, shell=True)
    time.sleep(2)

    if useCustomLogo:
        cmd = f"bin/irecovery -f bootlogo.img4"
        so = subprocess.Popen(cmd, shell=True)
        time.sleep(2)

        cmd = 'bin/irecovery -c "setpicture 0"'
        so = subprocess.Popen(cmd, shell=True)
        time.sleep(2)

        cmd = 'bin/irecovery -c "bgcolor 0 0 0"'
        so = subprocess.Popen(cmd, shell=True)
        time.sleep(2)

    cmd = "bin/irecovery -f devicetree.img4"
    so = subprocess.Popen(cmd, shell=True)
    time.sleep(2)

    cmd = 'bin/irecovery -c "devicetree"'
    so = subprocess.Popen(cmd, shell=True)
    print(so)  # For some weird reason, devicetree won't execute properly unless I print this?????? If I don't then I have to send devicetree/trustcache/kernel again after bootx fails
    time.sleep(2)

    if not '11.' in iosVersion:  # 11.x and lower don't need trustcache sent to boot =)

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

    cmd = f"bin/irecovery -m"
    so = subprocess.Popen(cmd, shell=True)
    time.sleep(10)

    if "Recovery Mode" in str(so):
        test = True
    else:
        test = False
    if test:
        if useCustomLogo:
            cmd = f"bin/irecovery -f bootlogo.img4"
            so = subprocess.Popen(cmd, shell=True)
            time.sleep(2)

            cmd = 'bin/irecovery -c "setpicture 0"'
            so = subprocess.Popen(cmd, shell=True)
            time.sleep(2)

            cmd = 'bin/irecovery -c "bgcolor 0 0 0"'
            so = subprocess.Popen(cmd, shell=True)
            time.sleep(2)

        cmd = "bin/irecovery -f devicetree.img4"
        so = subprocess.Popen(cmd, shell=True)
        time.sleep(2)

        cmd = 'bin/irecovery -c "devicetree"'
        so = subprocess.Popen(cmd, shell=True)
        print(so)  # For some weird reason, devicetree won't execute properly unless I print this?????? If I don't then I have to send devicetree/trustcache/kernel again after bootx fails
        time.sleep(2)

        if not '11.' in iosVersion:  # 11.x and lower don't need trustcache sent to boot =)

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


def img4stuff(deviceModel, iOSVersion, useCustomLogo, bootlogoPath, areWeLocal):
    api = ipswapi.APIParser(deviceModel, iOSVersion)

    print(f"Checking theiphonewiki for {iOSVersion} keys...")
    wiki = iphonewiki.iPhoneWiki(deviceModel, iOSVersion)
    keys = wiki.getWikiKeys()

    iBECName = keys["IBEC"]
    iBECKey = keys["IBECKEY"]
    iBECIV = keys["IBECIV"]

    iBSSName = keys["IBSS"]
    iBSSKey = keys["IBSSKEY"]
    iBSSIV = keys["IBSSIV"]
    if iBECIV == "Unknown":  # Just making sure that there is keys, some key pages have keys for one model but not the other which could cause issues
        print("Keys for the other device model are present but not for yours sorry\nFeel free to get them and add them to theiphonewiki =)")
        exit(2)

    ipswurl = api.printURLForArchive()

    # geting shsh
    print("Getting SHSH for signing images")
    so = subprocess.Popen(f"./resources/bin/tsschecker -d iPhone6,2 -e 12326262 -l -s", stdout=subprocess.PIPE, shell=True)
    output = so.stdout.read()
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

    if areWeLocal == False:

        print(f"Downloading and patching {iOSVersion}'s iBSS/iBEC")

        api.downloadFileFromArchive(f"Firmware/dfu/{iBECName}", "resources/ibec.im4p")

        api.downloadFileFromArchive(f"Firmware/dfu/{iBSSName}", "resources/ibss.im4p")

    else:
        # We need to move the correct iBSS/iBEC from IPSW/ to resources/
        print("Moving iBSS/iBEC...")
        shutil.move(f"IPSW/{iBECName}", "resources/ibec.im4p")
        shutil.move(f"IPSW/{iBSSName}", "resources/ibss.im4p")

    # Assuming that worked (add checks) we now need to decrpyt and patch iBSS/iBEC for booting
    so = subprocess.Popen(f"./resources/bin/img4tool -e -o resources/ibss.raw --iv {iBSSIV} --key {iBSSKey} resources/ibss.im4p", stdout=subprocess.PIPE, shell=True)
    output = so.stdout.read()
    if useCustomLogo:
        so = subprocess.Popen(f'./resources/bin/kairos resources/ibss.raw resources/ibss.pwn', stdout=subprocess.PIPE, shell=True)
        output = so.stdout.read()
    else:
        so = subprocess.Popen(f'./resources/bin/kairos resources/ibss.raw resources/ibss.pwn -b "-v"', stdout=subprocess.PIPE, shell=True)
        output = so.stdout.read()

    so = subprocess.Popen(f"./resources/bin/img4tool -e -o resources/ibec.raw --iv {iBECIV} --key {iBECKey} resources/ibec.im4p", stdout=subprocess.PIPE, shell=True)
    output = so.stdout.read()
    if useCustomLogo:
        so = subprocess.Popen(f'./resources/bin/kairos resources/ibec.raw resources/ibec.pwn', stdout=subprocess.PIPE, shell=True)
        output = so.stdout.read()
    else:
        so = subprocess.Popen(f'./resources/bin/kairos resources/ibec.raw resources/ibec.pwn -b "-v"', stdout=subprocess.PIPE, shell=True)
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

        if str(bootlogoPath).lower().endswith(".png"):
            so = subprocess.Popen(f"./resources/bin/ibootim {bootlogoPath} resources/bootlogo.ibootim", stdout=subprocess.PIPE, shell=True)  # Thanks to realnp for ibootim!
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
    if areWeLocal == False:
        print(f"Downloading {iOSVersion}'s BuildManifest.plist")
        try:
            api.downloadFileFromArchive("BuildManifest.plist", "resources/manifest.plist")
        except:
            print("ERROR: Failed to download BuildManifest.plist\nPlease re-run PyBoot again and it should work (might take a few tries)")
            exit(2)
    else:
        if os.path.exists("IPSW/BuildManifest.plist"):
            shutil.move("IPSW/BuildManifest.plist", "resources/manifest.plist")
        else:
            sys.exit("ERROR: Couldn't find local BuildManifest")
    line_number = 0
    with open("./resources/manifest.plist", mode="rt") as read_plist:
        for line in read_plist:
            line_number += 1
            if re.search("kernelcache.release.+", line):
                kernelname = line.rstrip()
                read_plist.close()
                break
    kernelname = kernelname[14:-9]
    if areWeLocal == False:

        print(f"Downloading {iOSVersion}'s KernelCache")
        try:
            api.downloadFileFromArchive(kernelname, "resources/kernel.im4p")
        except:
            print("ERROR: Failed to download Kernel\nPlease re-run PyBoot again and it should work (might take a few tries)")
            exit(2)
    else:
        if os.path.exists(f"IPSW/{kernelname}"):
            shutil.move(f"IPSW/{kernelname}", "resources/kernel.im4p")
        else:
            sys.exit("ERROR: Couldn't find local kernelcache")
    devicetreename = f"DeviceTree.{iBSSName[5:-13]}ap.im4p"
    if deviceModel == "iPhone6,2":
        devicetreename = "DeviceTree.n53ap.im4p"
    elif deviceModel == "iPhone6,1":
        devicetreename = "DeviceTree.n51ap.im4p"
    if areWeLocal == False:

        print(f"Downloading {iOSVersion}'s DeviceTree")
        try:
            api.downloadFileFromArchive(f"Firmware/all_flash/{devicetreename}", "resources/devicetree.im4p")
        except:
            print("ERROR: Failed to download DeviceTree\nPlease re-run PyBoot again and it should work (might take a few tries)")
            exit(2)
    else:
        if os.path.exists(f"IPSW/Firmware/all_flash/{devicetreename}"):
            shutil.move(f"IPSW/Firmware/all_flash/{devicetreename}", "resources/devicetree.im4p")
        else:
            sys.exit("ERROR: Couldn't find local devicetree")
    if areWeLocal == False:
        so = check_output(f"./resources/bin/pzb list {ipswurl}", shell=True)  # Need to check the downgraded IPSW to get the rootfs trustcache for booting
        so = str(so)
        rootfsoffset = so.find("GB") - 24  # This should always work, unless for some reason another file in the IPSW is > 1GB
        rootfsName = so[int(rootfsoffset):-51]  # This should be the correct number to cut from, will test more

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
                    api.downloadFileFromArchive(f'Firmware/{rootfsName}.trustcache', "resources/trustcache.im4p")
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
                    api.downloadFileFromArchive(f'Firmware/{rootfsName}.trustcache', "resources/trustcache.im4p")
                    time.sleep(5)
                else:
                    print("Start again from the beggining =)")
                    exit(2)
    else:
        # Find largest .dmg file in IPSW/ then add .trustcache to the end of the string
        
        objects = os.listdir("IPSW")

        sofar = 0
        name = ""

        for item in objects:
            if item.endswith(".dmg"):
                size = os.path.getsize(f"IPSW/{item}")
                if size > sofar:
                        sofar = size
                        name = item

        print(f"Largest file is {name}, getting correct trustcache...")
        trustcachename = f"{name}.trustcache"
        if os.path.exists(f"IPSW/Firmware/{trustcachename}"):
            shutil.move(f"IPSW/Firmware/{trustcachename}", "resources/trustcache.im4p")
        else:
            sys.exit("ERROR: Couldn't find local trustcache")

    # Can add a verification for after the patching to make sure it was applied correctly and in the right place just in case
    patchFiles(iOSVersion)
    print("Signing boot files")
    signImages()
