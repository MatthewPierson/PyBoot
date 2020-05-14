import os
import re
import shutil
import subprocess
import sys
import time
from subprocess import check_output
from resources.pwn import pwndfumode, decryptKBAG, pwndfumodeKeys

import requests

from resources.iospythontools import iphonewiki, ipswapi, utils

def patchThing():
    #Copyright (c) 2020, @mcg29_

    # Code used with permission from @mcg29_
    # Original code from: https://github.com/dualbootfun/dualbootfun.github.io/blob/master/source/compareFiles.py

	patched = open("resources/kernel.patched", "rb").read()
	original = open("resources/kernel.raw", "rb").read()
	lenP = len(patched)
	lenO = len(original)
	if lenP != lenO:
		print("size does not match, can't compare files! exiting...")
		sys.exit(1)
	diff = []
	for i in range(lenO):
		originalByte = original[i]
		patchedByte = patched[i]
		if originalByte != patchedByte:
			diff.append([hex(i),hex(originalByte), hex(patchedByte)])	
	diffFile = open('resources/kc.bpatch', 'w+')
	diffFile.write('#AMFI\n\n')
	for d in diff:
		data = str(d[0]) + " " + (str(d[1])) + " " + (str(d[2]))
		diffFile.write(data+ '\n')
		print(data)

def signImages():
    print("Signing boot files")
    # time to sign shit
    so = subprocess.Popen(f"./resources/bin/img4tool -c resources/devicetree.img4 -p resources/devicetree.im4p -s resources/shsh.shsh", stdout=subprocess.PIPE, shell=True)
    output = so.stdout.read()

   # if os.path.exists("resources/aopfw.im4p"):
        #so = subprocess.Popen(f"./resources/bin/img4tool -c resources/aopfw.img4 -p resources/aopfw.im4p -s resources/shsh.shsh", stdout=subprocess.PIPE, shell=True)
        #output = so.stdout.read()

    so = subprocess.Popen(f"./resources/bin/img4tool -c resources/kernel.img4 -p resources/kernel.im4p -s resources/shsh.shsh", stdout=subprocess.PIPE, shell=True)
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

    # I send the shsh file first just because some devices need a *dummmy* file to be sent before ibss in order to work

    cmd = "bin/irecovery -f shsh.shsh"
    so = subprocess.Popen(cmd, shell=True)
    time.sleep(2)

    cmd = "bin/irecovery -f ibss.img4"
    so = subprocess.Popen(cmd, shell=True)
    time.sleep(2)

    cmd = "bin/irecovery -f ibec.img4"
    so = subprocess.Popen(cmd, shell=True)
    time.sleep(5)

    cmd = 'bin/irecovery -c "bootx"'  # Is needed to prevent Devicetree related issues later on
    so = subprocess.Popen(cmd, shell=True)
    time.sleep(2)

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
    time.sleep(2)

    #if '13.' in iosVersion:  
        
     #   cmd = "bin/irecovery -f aopfw.img4"
      #  so = subprocess.Popen(cmd, shell=True)
       # time.sleep(2)

        #cmd = 'bin/irecovery -c "firmware"'
        #so = subprocess.Popen(cmd, shell=True)
        #time.sleep(2)

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

    os.chdir("../")


def img4stuff(deviceModel, iOSVersion, useCustomLogo, bootlogoPath, areWeLocal, bootOtherOS, bootArgs, amfiPatches):

    api = ipswapi.APIParser(deviceModel, iOSVersion)

    print(f"Checking theiphonewiki for {iOSVersion} keys...")
    wiki = iphonewiki.iPhoneWiki(deviceModel, iOSVersion)
    keys = wiki.getWikiKeys()
    if 'failed' in keys:
        print("Keys weren't found for your device, PyBoot will place your device into PWNDFU mode and retrieve the needed keys...\n")
        print("Please ensure your device is connected in DFU mode...")
        time.sleep(5)
        pwndfumodeKeys()
        needKeys = True
    else:

        needKeys = False

        iBECName = keys["IBEC"]
        iBECKey = keys["IBECKEY"]
        iBECIV = keys["IBECIV"]

        iBSSName = keys["IBSS"]
        iBSSKey = keys["IBSSKEY"]
        iBSSIV = keys["IBSSIV"]
        if iBECIV == "Unknown":  # Just making sure that there is keys, some key pages have keys for one model but not the other which could cause issues
            print("Keys for the other device model are present but not for your model.\nPyBoot will place your device into PWNDFU mode and retrieve the needed keys...")
            print("Please ensure your device is connected in DFU mode...")
            time.sleep(5)
            pwndfumodeKeys()
            needKeys = True

    ipswurl = api.printURLForArchive()

    # geting shsh
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
    if needKeys:
        line_number = 0
        count = 0
        thing = False
        models = []
        with open("./resources/manifest.plist", mode="rt") as read_plist:
            for line in read_plist:
                line_number += 1
                if thing == True:
                    deviceModel = line.rstrip()
                    models.append(deviceModel)
                    thing = False
                    if count == 2:
                        break
                if re.search("DeviceClass", line):
                    line_number += 1
                    thing = True
                    count += 1
            read_plist.close()

        choice1 = models[0]
        choice2 = models[1]
        choice1 = str(choice1.strip('\t\t\t'))
        choice2 = str(choice2.strip('\t\t\t'))
        choice1 = choice1[8:-9]
        choice2 = choice2[8:-9]
        print(f"Found multiple device models...\nWhich is your device?\n")
        print(f"1: {choice1}\n2: {choice2}\n")
        modelchoice = input("Enter 1 or 2: ")
        if modelchoice == "1":
            print(f"Device set to {choice1}")
            iBECName = f"iBEC.{choice1[:-2]}.RELEASE.im4p"
            iBSSName = f"iBSS.{choice1[:-2]}.RELEASE.im4p"
        elif modelchoice == "2":
            print(f"Device set to {choice2}")
            iBECName = f"iBEC.{choice2[:-2]}.RELEASE.im4p"
            iBSSName = f"iBSS.{choice2[:-2]}.RELEASE.im4p"
        else:
            print("Invalid input...\nExiting...")
            exit(0)
    print("Getting SHSH for signing images")
    so = subprocess.Popen(f"./resources/bin/tsschecker -d iPhone6,2 -e 85888280a402e -l -s", stdout=subprocess.PIPE, shell=True)
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
        test = False

    else:
        # We need to move the correct iBSS/iBEC from IPSW/ to resources/
        print("Moving iBSS/iBEC...")
        shutil.move(f"IPSW/{iBECName}", "resources/ibec.im4p")
        shutil.move(f"IPSW/{iBSSName}", "resources/ibss.im4p")

    if needKeys:
        so = subprocess.Popen("./resources/bin/img4tool -a resources/ibss.im4p", stdout=subprocess.PIPE, shell=True)
        output = so.stdout.read()
        output = output.decode("utf-8")

        offset1 = output.find("num: 1")
        offset2 = output.find("num: 2")
        offset1 += 7
        iBSSKBAG = output[offset1:offset2]
        iBSSKBAG = iBSSKBAG.strip('\n')
        iBSSKBAG = iBSSKBAG[0 : 32 : ] + iBSSKBAG[32 + 1 : :]

        so = subprocess.Popen("./resources/bin/img4tool -a resources/ibec.im4p", stdout=subprocess.PIPE, shell=True)
        output = so.stdout.read()
        output = output.decode("utf-8")

        offset1 = output.find("num: 1")
        offset2 = output.find("num: 2")
        offset1 += 7
        iBECKBAG = output[offset1:offset2]
        iBECKBAG = iBECKBAG.strip(  '\n')
        iBECKBAG = iBECKBAG[0 : 32 : ] + iBECKBAG[32 + 1 : :]

        ibssIVKEY = decryptKBAG(iBSSKBAG)
        ibecIVKEY = decryptKBAG(iBECKBAG)

        if len(ibssIVKEY) != 96 or len(ibecIVKEY) != 96:
            print(ibssIVKEY)
            print(ibecIVKEY)
            sys.exit('String provided is not 96 bytes!')
        else:
            iBSSIV = ibssIVKEY[:32]
            iBSSKey = ibssIVKEY[-64:]
            iBECIV = ibecIVKEY[:32]
            iBECKey = ibecIVKEY[-64:]

        print("\n\nDevice needs to be rebooted in order to continue, please re-enter DFU mode and then press enter to continue...")
        print("If you do not reboot the device into DFU mode, PyBoot will fail to send the needed boot components")
        print("Waiting for user to press enter...")
        input()

    patcher = "kairos" # Just allows me to change what boot image patcher I use with ease (mainly for A11 tests)
    if test:
        print("Fuck this")
        iBSSIV = "b4cb3336374505028c995acb9a565c45"
        iBSSKey = "877ce08c24e42ecf582d60719648ef4ef915809e1b0ccff518f5db3004a806ce"
        iBECIV = "8358a6ae2d477357a2f1eabc0287ddcb"
        iBECKey = "72fb077f67f61141cb4224ee0ed6e9a43578c13922937fc91d23ed4949862132"
    so = subprocess.Popen(f"./resources/bin/img4tool -e -o resources/ibss.raw --iv {iBSSIV} --key {iBSSKey} resources/ibss.im4p", stdout=subprocess.PIPE, shell=True)
    output = so.stdout.read()    
    if useCustomLogo:
        if bootOtherOS:
            so = subprocess.Popen(f'./resources/bin/{patcher} resources/ibss.raw resources/ibss.pwn -b "{bootArgs}"', stdout=subprocess.PIPE, shell=True)
            output = so.stdout.read()
        else:
            so = subprocess.Popen(f'./resources/bin/{patcher} resources/ibss.raw resources/ibss.pwn', stdout=subprocess.PIPE, shell=True)
            output = so.stdout.read()
    else:
        so = subprocess.Popen(f'./resources/bin/{patcher} resources/ibss.raw resources/ibss.pwn -b "{bootArgs}"', stdout=subprocess.PIPE, shell=True)
        output = so.stdout.read()

    so = subprocess.Popen(f"./resources/bin/img4tool -e -o resources/ibec.raw --iv {iBECIV} --key {iBECKey} resources/ibec.im4p", stdout=subprocess.PIPE, shell=True)
    output = so.stdout.read()
    if useCustomLogo:
        if bootOtherOS:
            so = subprocess.Popen(f'./resources/bin/{patcher} resources/ibec.raw resources/ibec.pwn -b "{bootArgs}"', stdout=subprocess.PIPE, shell=True)
            output = so.stdout.read()
        else:
            so = subprocess.Popen(f'./resources/bin/{patcher} resources/ibec.raw resources/ibec.pwn', stdout=subprocess.PIPE, shell=True)
            output = so.stdout.read()
    else:
        so = subprocess.Popen(f'./resources/bin/{patcher} resources/ibec.raw resources/ibec.pwn -b "{bootArgs}"', stdout=subprocess.PIPE, shell=True)
        output = so.stdout.read()
    if bootOtherOS and "13." in iOSVersion:
        # Excuse the long byte strings, just want to be sure that we patch the correct thing :)
        bootpartitionString = b"\x30\x00\x2F\x53\x79\x73\x74\x65\x6D\x2F\x4C\x69\x62\x72\x61\x72\x79\x2F\x43\x61\x63\x68\x65\x73\x2F\x63\x6F\x6D\x2E\x61\x70\x70\x6C\x65\x2E\x6B\x65\x72\x6E\x65\x6C\x63\x61\x63\x68\x65\x73\x2F\x6B\x65\x72\x6E\x65\x6C\x63\x61\x63\x68\x65"
        bootpartitionPatch = b"\x35"
        if os.path.isfile("resources/ibec.pwn"):
            print("Patching boot-partition from 0 to 5")
            with open("resources/ibec.pwn", "r+b") as fh:
                file = fh.read()
                try:
                    offset = hex(file.index(bootpartitionString))  # getting offset for start of string
                    offset = int(offset, 16)
                    fh.seek(offset, 0)
                    fh.write(bootpartitionPatch)  # writing 5 so we can boot the system partition
                    fh.close()
                    print("boot-partition patch complete")
                except:
                    print("iBEC patching failed!")
                    exit(2)

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
        if (os.path.exists("resources/bootlogo.png")):
            so = subprocess.Popen(f"./resources/bin/ibootim resources/bootlogo.png resources/bootlogo.ibootim", stdout=subprocess.PIPE, shell=True)  # Thanks to realnp for ibootim!
            output = so.stdout.read()
            # now create im4p
            so = subprocess.Popen(f"./resources/bin/img4tool -c resources/bootlogo.im4p -t logo resources/bootlogo.ibootim", stdout=subprocess.PIPE, shell=True)
            output = so.stdout.read()
            # Add signature from shsh
            so = subprocess.Popen(f"./resources/bin/img4tool -c resources/bootlogo.img4 -p resources/bootlogo.im4p -s resources/shsh.shsh", stdout=subprocess.PIPE, shell=True)
            output = so.stdout.read()
            bootlogoPath = "resources/bootlogo.img4"
        else:
            print("Please either add your own image to ./resources/bootlogo.png or redownload the one that comes with PyBoot")
            exit(0)
    # iBSS/iBEC stuff is done, we now need to get devicetree, trustcache and kernel
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
            if deviceModel == "iPhone8,4":
                kernelname = "kernelcache.release.iphone8b"
            api.downloadFileFromArchive(kernelname, "resources/kernel.im4p")
        except:
            print("ERROR: Failed to download Kernel\nPlease re-run PyBoot again and it should work (might take a few tries)")
            exit(2)
    else:
        if os.path.exists(f"IPSW/{kernelname}"):
            shutil.move(f"IPSW/{kernelname}", "resources/kernel.im4p")
        else:
            sys.exit("ERROR: Couldn't find local kernelcache")
    if amfiPatches:
        print("Applying AMFI patches to kernel (Thanks to Ralph and mcg29_)")
        so = subprocess.Popen(f"./resources/bin/img4 -i resources/kernel.im4p -o resources/kernel.raw", stdout=subprocess.PIPE, shell=True)
        output = so.stdout.read()
        time.sleep(5)
        if os.path.exists("resources/kernel.raw"):
            print("Saved raw kernel to 'resources/kernel.raw'")
            so = subprocess.Popen(f"./resources/bin/Kernel64Patcher resources/kernel.raw resources/kernel.patched -a", stdout=subprocess.PIPE, shell=True)
            output = so.stdout.read()
            patchThing()
            so = subprocess.Popen(f"./resources/bin/img4tool -e -s resources/shsh.shsh -m resources/IM4M", stdout=subprocess.PIPE, shell=True)
            output = so.stdout.read()
            print("Patched AMFI from kernel")
            so = subprocess.Popen(f"./resources/bin/img4 -i resources/kernel.im4p -o resources/kernel.img4 -M resources/IM4M -T krnl -P resources/kc.bpatch", stdout=subprocess.PIPE, shell=True)
            output = so.stdout.read()
            print("Finished patching kernel!\nContinuing with PyBoot...\n")
        else:
            print("Failed to extract raw kernel, continuing without AMFI kernel patches...")

    devicetreename = f"DeviceTree.{iBSSName[5:-13]}ap.im4p"
    if deviceModel == "iPhone6,2":
        devicetreename = "DeviceTree.n53ap.im4p"
    elif deviceModel == "iPhone6,1":
        devicetreename = "DeviceTree.n51ap.im4p"
    elif deviceModel == "iPad7,5":
        devicetreename = "DeviceTree.j71bap.im4p"
    elif deviceModel == "iPad7,6":
        devicetreename = "DeviceTree.j72bap.im4p"
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

    if bootOtherOS and "13." in iOSVersion:

        #api.downloadFileFromArchive(f"Firmware/AOP/aopfw-s8000aop.im4p", "resources/aopfw.im4p")

        print("Patching Devicetree to allow for new Data partition to be mounted (13.x Only)...")
        # Unpack devicetree so Ralph's patcher will work
        so = subprocess.Popen(f"./resources/bin/img4tool -e -o resources/devicetree.raw resources/devicetree.im4p", stdout=subprocess.PIPE, shell=True)
        output = so.stdout.read()
        # Patch it
        so = subprocess.Popen(f"./resources/bin/dtree_patcher resources/devicetree.raw resources/devicetree.patched -d", stdout=subprocess.PIPE, shell=True)
        output = so.stdout.read()
        # Repack it to im4p
        so = subprocess.Popen(f"./resources/bin/img4tool -c resources/devicetree.im4p -t dtre resources/devicetree.patched", stdout=subprocess.PIPE, shell=True)
        output = so.stdout.read()
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
                print(f"\nFailed to get RootFS name\nPlease look up the RootFS filename on the key page for {deviceModel} - iOS {iOSVersion} theiphonewiki and type it here then press enter:\n")
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
    signImages()
