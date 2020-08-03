import os
import subprocess
import time
import shutil
import requests
import re
import stat

from zipfile import ZipFile, is_zipfile
from resources.ipwndfu import checkm8, dfu, usbexec

def decryptKBAG(kbag: str):

    device = dfu.acquire_device()
    serial_number = device.serial_number
    dfu.release_device(device)
    if "CPID:8960" in serial_number or "CPID:8965" in serial_number or "CPID:8010" in serial_number or "CPID:8015" in serial_number:
        cmd = f'resources/ipwndfuX/ipwndfu --decrypt-gid={kbag}' # Tried to port the function to python3 but was far to difficult for some reason
    elif "CPID:8000" in serial_number or "CPID:8003" in serial_number or "CPID:7000" in serial_number or "CPID:7001" in serial_number:
        cmd = f'resources/ipwndfuKeys/ipwndfu --decrypt-gid={kbag}' # Tried to port the function to python3 but was far to difficult for some reason
    else:
        print("Not supported...")
        exit(0)
    ivkey = os.popen(cmd).read()
    ivkey = re.sub(r'Decrypting with \w+ GID key\.', '', ivkey)
    ivkey = ivkey[1:-1]

    return ivkey

def pwndfumodeKeys():

    device = dfu.acquire_device()
    serial_number = device.serial_number
    dfu.release_device(device)

    if "CPID:8960" in serial_number:
        if not os.path.exists("checkm8.py"):
            os.chdir("resources/ipwndfu")
        runexploit = checkm8.exploit()
        if runexploit:
            os.chdir("../..")
        else:
            print("Exploit failed, reboot device into DFU mode and press enter to re-run checkm8")
            input()
            pwndfumodeKeys  ()
    elif "CPID:8965" in serial_number:
        if not os.path.exists("checkm8.py"):
            os.chdir("resources/ipwndfu")
        runexploit = checkm8.exploit()
        if runexploit:
            print("Exploit worked!")
            os.chdir("../..")
        else:
            print("Exploit failed, reboot device into DFU mode and press enter to re-run checkm8")
            input()
            pwndfumodeKeys()
    elif "CPID:8010" in serial_number:
        if "PWND:[checkm8]" in serial_number:
            print("Device already in PWNDFU mode, not re-running exploit..")
            return
        else:
            if not os.path.exists("checkm8.py"):
                os.chdir("resources/ipwndfu8010")
            cmd = './ipwndfu -p'
            so = os.popen(cmd).read()
            print(so)
            if "ERROR: No Apple device" in so:
                print("Exploit failed, reboot device into DFU mode and press enter to re-run checkm8")
                input()
                pwndfumodeKeys()
            time.sleep(5)
            device = dfu.acquire_device()
            serial_number = device.serial_number
            dfu.release_device(device)
            if "PWND:[checkm8]" in serial_number:
                print("Exploit worked!")
                os.chdir("../..")
                time.sleep(5)
                return

    elif "CPID:8015" in serial_number:
        if "PWND:[checkm8]" in serial_number:
            print("Device already in PWNDFU mode, not re-running exploit..")
            return
        else:
            if not os.path.exists("checkm8.py"):
                os.chdir("resources/ipwndfuX")
            cmd = './ipwndfu -p'
            so = os.popen(cmd).read()
            print(so)
            if "ERROR: No Apple device" in so:
                print("Exploit failed, reboot device into DFU mode and press enter to re-run checkm8")
                input()
                pwndfumodeKeys()
            os.chdir("../..")
            time.sleep(5)
            # Need to re-acquire the device before we check if checkm8 worked or it will always report as failed
            device = dfu.acquire_device()
            serial_number = device.serial_number
            dfu.release_device(device)
            if "PWND:[checkm8]" in serial_number:
                print("Exploit worked!")
                return
            else:
                print("Exploit failed...\nReboot and try again...")
                exit(2)
    elif "CPID:8000" in serial_number or "CPID:8003" in serial_number or "CPID:7000" in serial_number or "CPID:7001" in serial_number:
        if "PWND:[checkm8]" in serial_number:
            print("Device already in PWNDFU mode, not re-running exploit..")
            return
        else:
            if not os.path.exists("checkm8.py"):
                os.chdir("resources/ipwndfuKeys")
            cmd = './ipwndfu -p'
            so = os.popen(cmd).read()
            print(so)
            if "ERROR: No Apple device" in so:
                print("Exploit failed, reboot device into DFU mode and press enter to re-run checkm8")
                input()
                pwndfumodeKeys()
            os.chdir("../..")
            time.sleep(5)
            # Need to re-acquire the device before we check if checkm8 worked or it will always report as failed
            device = dfu.acquire_device()
            serial_number = device.serial_number
            dfu.release_device(device)
            if "PWND:[checkm8]" in serial_number:
                print("Exploit worked!")
                return
            else:
                print("Exploit failed...\nReboot and try again...")
                exit(2)
        return
    else:
        print("Please open an issue and let me know what device you are using/it's CPID and I will add support ASAP")
        exit(2)


def pwndfumode():

    device = dfu.acquire_device()
    serial_number = device.serial_number
    dfu.release_device(device)

    if "CPID:8960" in serial_number:
        if not os.path.exists("checkm8.py"):
            os.chdir("resources/ipwndfu")
        runexploit = checkm8.exploit()
        if runexploit:
            print("Exploit worked!")
            cmd = 'python2.7 rmsigchks.py'
            so = os.popen(cmd).read()
            print(so)
            os.chdir("../..")
        else:
            print("Exploit failed, reboot device into DFU mode and press enter to re-run checkm8")
            input()
            pwndfumode()
    elif "CPID:8965" in serial_number:
        if not os.path.exists("checkm8.py"):
            os.chdir("resources/ipwndfu")
        runexploit = checkm8.exploit()
        if runexploit:
            print("Exploit worked!")
            cmd = 'python2.7 rmsigchks.py'
            so = os.popen(cmd).read()
            print(so)
            os.chdir("../..")
        else:
            print("Exploit failed, reboot device into DFU mode and press enter to re-run checkm8")
            input()
            pwndfumode()
    elif "CPID:8010" in serial_number:

        # I don't want to bundle Fugu just to make sure that people know it hasnt been modified 
        # I'd rather just quickly download the binary from Linus's github if it hasnt been already to avoid any issues

        if os.path.exists("resources/Fugu_8010/Fugu"):
            pass
        else:
            os.mkdir("resources/Fugu_8010")

            print("Downloading latest Fugu release from LinusHenze's github...")
                
            if os.path.exists("fugu.zip"):
                os.remove("fugu.zip")

            url = "https://github.com/LinusHenze/Fugu/releases/download/v0.4/Fugu_v0.4.zip"
            r = requests.get(url, allow_redirects=True)

            open('fugu.zip', 'wb').write(r.content)

            if os.path.exists("fugu"):
                shutil.rmtree("fugu")
                os.mkdir("fugu")
            else:
                os.mkdir("fugu")
            
            shutil.move("fugu.zip", "fugu/fugu.zip")
            os.chdir("fugu")

            with ZipFile('fugu.zip', 'r') as zipObj:
                
                zipObj.extractall()
            
            os.chdir("../")

            shutil.move("fugu/fugu", "resources/Fugu_8010/Fugu")
            shutil.move("fugu/shellcode", "resources/Fugu_8010/shellcode")

            st = os.stat('resources/Fugu_8010/Fugu')
            os.chmod('resources/Fugu_8010/Fugu', st.st_mode | stat.S_IEXEC)

            shutil.rmtree("fugu")

            print("Fugu has now been installed!")

        if "PWND:[checkm8]" in serial_number:
            print("Device already in PWNDFU mode, not re-running exploit..")
            return
        else:
            if not os.path.exists("Fugu"):
                os.chdir("resources/Fugu_8010")
            cmd = './Fugu rmsigchks'
            so = os.popen(cmd).read()
            #print(so)
            if "Exploiting iDevice: FAILED!" in so:
                print("Exploit failed, however re-expoilting without rebooting might work. Attempting now...")
                pwndfumode()
            if "Device could not be found!" in so:
                print("Exploit failed, reboot device into DFU mode and press enter to re-run checkm8")
                input()
                pwndfumode()
            time.sleep(5)
            device = dfu.acquire_device()
            serial_number = device.serial_number
            dfu.release_device(device)
            if "PWND:[checkm8]" in serial_number:
                print("Exploit worked!")
                os.chdir("../..")
                time.sleep(5)
                return

    elif "CPID:8015" in serial_number:
        if "PWND:[checkm8]" in serial_number:
            print("Device already in PWNDFU mode, not re-running exploit..")
            return
        else:
            if not os.path.exists("checkm8.py"):
                os.chdir("resources/ipwndfuX")
            cmd = './ipwndfu -p'
            so = os.popen(cmd).read()
            print(so)
            if "ERROR: No Apple device" in so:
                print("Exploit failed, reboot device into DFU mode and press enter to re-run checkm8")
                input()
                pwndfumode()
            cmd = './ipwndfu --patch'
            so = os.popen(cmd).read()
            print(so)
            os.chdir("../..")
            time.sleep(5)
            # Need to re-acquire the device before we check if checkm8 worked or it will always report as failed
            device = dfu.acquire_device()
            serial_number = device.serial_number
            dfu.release_device(device)
            if "PWND:[checkm8]" in serial_number:
                print("Exploit worked!")
                return
            else:
                print("Exploit failed...\nReboot and try again...")
                exit(2)
    elif "CPID:8000" in serial_number:
        cmd = './resources/bin/eclipsa8000'
        so = os.popen(cmd).read()
        print(so)
        print("Eclipsa doesn't allow me to see if the exploit worked or not =(\nJust have to assume it did, if it didn't then reboot into DFU mode and re-run PyBoot")
        return
    elif "CPID:8003" in serial_number:
        cmd = './resources/bin/eclipsa8003'
        so = os.popen(cmd).read()
        print(so)
        print("Eclipsa doesn't allow me to see if the exploit worked or not =(\nJust have to assume it did, if it didn't then reboot into DFU mode and re-run PyBoot")
        return
    elif "CPID:7000" in serial_number:
        cmd = './resources/bin/eclipsa7000'
        so = os.popen(cmd).read()
        print(so)
        print("Eclipsa doesn't allow me to see if the exploit worked or not =(\nJust have to assume it did, if it didn't then reboot into DFU mode and re-run PyBoot")
        return
    elif "CPID:7001" in serial_number:
        cmd = './resources/bin/eclipsa8000'
        so = os.popen(cmd).read()
        print(so)
        print("Eclipsa doesn't allow me to see if the exploit worked or not =(\nJust have to assume it did, if it didn't then reboot into DFU mode and re-run PyBoot")
        return
    else:
        print("Please open an issue and let me know what device you are using/it's CPID and I will add support ASAP")
        exit(2)
