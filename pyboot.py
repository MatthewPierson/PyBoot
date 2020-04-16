#!/usr/bin/env python3

import subprocess
from subprocess import check_output
import sys

try:

    import argparse
    import os
    import platform
    import plistlib
    import re
    import shutil
    import time
    from argparse import RawTextHelpFormatter
    from resources import img4, pwn, ipsw
    from resources.iospythontools import iphonewiki, ipswapi, utils

except:
    print("Failed to import dependencies, running pip to install them...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    try:
        import argparse
        import os
        import platform
        import plistlib
        import re
        import shutil
        import time
        from subprocess import check_output
        from argparse import RawTextHelpFormatter
        from resources import img4, pwn, ipsw
        from resources.iospythontools import iphonewiki, ipswapi, utils
        
    except:
        print("\n\nFailed to install dependencies, please manually run 'pip3 install -r requirements.txt' then re-run PyBoot") # Simplest way to make sure the user knows what to do if they haven't installed dependencies yet
        exit(0)
    print("\n\nSuccessfully installed dependencies!\n\nContinuing with PyBoot...\n")



tool_version = '\033[92m' + "Beta 0.5" + '\033[0m'


def main():
    removeFiles = [
        'resources/devicetree.im4p',
        'resources/devicetree.img4',
        'resources/ibec.im4p',
        'resources/ibec.img4',
        'resources/ibec.raw',
        'resources/ibec.pwn',
        'resources/ibec.patched',
        'resources/ibss.im4p',
        'resources/ibss.img4',
        'resources/ibss.raw',
        'resources/ibss.pwn',
        'resources/ibss.patched',
        'resources/kernel.im4p',
        'resources/kernel.img4',
        'resources/manifest.plist',
        'resources/shsh.shsh',
        'resources/trustcache.im4p',
        'resources/trustcache.img4',
        'resources/bootlogo.im4p',
        'resources/bootlogo.ibootim',
        "resources/bootlogo.img4"
    ]

    for item in removeFiles: # removes files from above list
        if os.path.isfile(item):
            os.remove(item)

    utils.clean() # removes potentially out of date JSON files 

    text = 'PyBoot - A tool for tether booting Checkm8 vulnerable iOS devices by Matty, @mosk_i.'
    parser = argparse.ArgumentParser(description=text, formatter_class=RawTextHelpFormatter, usage=f"./pyboot.py -i 'DEVICE IOS'\n\nE.G './pyboot.py -i iPhone9,2 13.2.3 -b ~/Downloads/bootlogo.png'\n\nCurrent PyBoot version is: {tool_version}", epilog="EXAMPLE USAGE: ./pyboot.py -i iPhone8,1 13.4.1 -d disk0s1s6\n\nOR ./pyboot -i iPhone9,4 13.1.3 -b ~/Downloads/bootlogo.png\n\nOR ./pyboot -q ~/Downloads/13.2.3.iPhone7.ipsw iPhone9,1 -a")
    parser.add_argument("-i", "--ios", help="iOS version you wish to boot (DEVICE IOS)", nargs=2, metavar=('\b', '\b'))
    parser.add_argument("-q", "--ipsw", help="Path to downloaded IPSW (PATH DEVICE)", nargs=2, metavar=('\b', '\b'))
    parser.add_argument("-b", "--bootlogo", help="Path to .PNG you wish to use as a custom Boot Logo (LOGO)", nargs=1, metavar=("\b"))
    parser.add_argument('-p', '--pwn', help='Enter PWNDFU mode, which will also apply signature patches', action='store_true')
    parser.add_argument("-d", "--dualboot", help="Name of system partition you wish to boot (e.g disk0s1s3 or disk0s1s6)", nargs=1, metavar=("\b"))
    parser.add_argument("-a", "--bootargs", help="Custom boot-args, will prompt user to enter, don't enter a value upon running PyBoot (Default is '-v')", action='store_true')
    parser.add_argument("-v", "--version", help="List the version of the tool", action="store_true")
    parser.add_argument("-c", "--credits", help="List credits", action="store_true")

    if platform.system() == 'Darwin':  # If not MacOS then exit basically
        pass
    elif platform.system() == "Linux":
        sys.exit('\033[91m' + "\nSorry this OS is not currently supported!\n\nOnly MacOS machines (Hackintosh or a legitimate Apple computer) are support as of now.\n" + '\033[0m')
    elif platform.system() == "Windows":
        sys.exit('\033[91m' + "\nSorry Windows will never be supported!\n\nOnly MacOS machines (Hackintosh or a legitimate Apple computer) are support as of now.\n" + '\033[0m')
    else:
        sys.exit("Wtf are you even running this on?")

    args = parser.parse_args()

    if args.credits:
        print('\033[95m' + "\nCreated by: Matty - @mosk_i\n" + '\033[0m')
        print('\033[94m' + "Other parts by -\n" + '\033[0m')
        print('\033[92m' + "Thimstar - [img4tool]")
        print("realnp - [ibootim]")
        print("axi0mX - [ipwndfu/checkm8]")
        print("dayt0n - [kairos]")
        print("Marco Grassi - [PartialZip]")
        print("Merculous - [ios-python-tools]")
        print("0x7ff - [Eclipsa]")
        print("libimobiledevice team - [irecovery]\n" + '\033[0m')
        sys.exit()
    elif args.pwn:
        pwn.pwndfumode()
        exit(22)
        
    elif args.ipsw:
        if args.bootlogo:
            useCustomLogo = True
            logopath = args.bootlogo[0]
        else:
            useCustomLogo = False
            logopath = "null"
        if args.dualboot:
            bootOtherOS = True
            sysPartName = args.dualboot[0]
            bootArgs = f"rd={sysPartName} -v"
            if args.bootargs:
                print(f"\n" + '\033[93m' + "WARNING:" + '\033[0m' + f"'-a' was specified indicating the user wanted to set custom boot-args, but '-d' was also set which currently doesn't support custom boot-args...\nIgnoring '-a' and continuing with '{bootArgs}' as the set boot-args.\n")
        else:
            bootOtherOS = False
            if args.bootargs:
                bootArgs = input("Please enter the boot-args you want to use then press enter: ")
            else:
                bootArgs = "-v"
        
            
        print('\033[95m' + "PyBoot - A tool for tether booting Checkm8 vulnerable iOS devices by Matty, @mosk_i\n" + '\033[0m')
        print("Current version is: " + tool_version)
        print("User chose to use a locally stored IPSW, running some checks...")
        if os.path.exists("IPSW"):
            shutil.rmtree("IPSW")
        ipsw.unzipIPSW(args.ipsw[0])
        version = False
        supportedModels = str(ipsw.readmanifest("IPSW/BuildManifest.plist", version))
        if args.ipsw[1] in supportedModels:
            print("IPSW is for given device!")
        else:
            print("Sorry this IPSW is not valid for the given device, either run PyBoot with -i to download the correct files or download the correct ipsw from ipsw.me")
            exit(0)
        version = True
        iosVersion = str(ipsw.readmanifest("IPSW/BuildManifest.plist", version))
        print(f"iOS version is: {iosVersion} and device model is: {args.ipsw[1]}")
        time.sleep(5)

        arewelocal = True
        img4.img4stuff(args.ipsw[1], iosVersion, useCustomLogo, logopath, arewelocal, bootOtherOS, bootArgs)

        # now to pwn device
        print("Exploiting device with checkm8")
        pwn.pwndfumode()

        # Send files to device and boot =)
        img4.sendImages(iosVersion, useCustomLogo)

        print("Device should be booting!")
        exit(0)
    elif args.ios:
        print('\033[95m' + "PyBoot - A tool for tether booting Checkm8 vulnerable iOS devices by Matty, @mosk_i\n" + '\033[0m')
        print("Current version is: " + tool_version)
        if args.bootlogo:
            useCustomLogo = True
            logopath = args.bootlogo[0]
        else:
            useCustomLogo = False
            logopath = "null"
        if args.dualboot:
            bootOtherOS = True
            sysPartName = args.dualboot[0]
            bootArgs = f"rd={sysPartName} -v"
            print(f"User choose to boot {args.ios[1]} from /dev/{sysPartName}.")
            if args.bootargs:
                print(f"\n" + '\033[93m' + "WARNING:" + '\033[0m' + f"'-a' was specified indicating the user wanted to set custom boot-args, but '-d' was also set which currently doesn't support custom boot-args...\nIgnoring '-a' and continuing with '{bootArgs}' as the set boot-args.\n")
        else:
            bootOtherOS = False
            if args.bootargs:
                bootArgs = input("Please enter the boot-args you want to use then press enter: ")
            else:
                bootArgs = "-v"

        if "10." in (str(args.ios))[2:-2]:
            print("\nWARNING - 10.x Currently WILL NOT BOOT. You can try if you want to but expect it not to boot!\nPress enter to continue or type anything else and press enter to exit")
            choice = input("")
            if choice == "":
                pass
            else:
                print("Exiting...")
                exit(2)

        print("Make sure your device is connected in DFU mode")
        time.sleep(5)
        arewelocal = False
        img4.img4stuff(args.ios[0], args.ios[1], useCustomLogo, logopath, arewelocal, bootOtherOS, bootArgs)

        # now to pwn device
        print("Exploiting device with checkm8")
        pwn.pwndfumode()

        # Send files to device and boot =)
        img4.sendImages(args.ios[1], useCustomLogo)

        print("Device should be booting!")
        exit(2)

    elif args.version:
        sys.exit(f"Current version is: {tool_version}")

    else:
        sys.exit(parser.print_help(sys.stderr))


if __name__ == "__main__":
    main()
