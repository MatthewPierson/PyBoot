#!/usr/bin/env python3

import argparse
import os
import platform
import plistlib
import re
import shutil
import subprocess
import sys
import time
from subprocess import check_output

from resources import img4, pwn
from resources.iospythontools import iphonewiki, ipswapi, utils

try:

    from PIL import Image

except:
    print("Failed to import dependencies, please run 'pip3 install -r requirements.txt' then re-run PyBoot")
    exit(2)


tool_version = '\033[92m' + "Beta 0.1" + '\033[0m'  # Leave outside so we have it at an obvious spot to find later

"""
unsupportedDevices = [
    'iPhone8,2',  # No keys at all
    'iPhone7,1',  # No keys at all
    'iPhone8,4',  # No keys at all
    'iPhone10,1',  # Can't test and don't want to add support till its confirmed to work
    'iPhone10,2',  # Can't test and don't want to add support till its confirmed to work
    'iPhone10,3',  # Can't test and don't want to add support till its confirmed to work
    'iPhone10,4',  # Can't test and don't want to add support till its confirmed to work
    'iPad5,1',
    'iPad5,2',
    'iPad5,3',
    'iPad5,3',
    'iPad7,1',
    'iPad7,2',
    'iPad7,3',
    'iPad7,4',
    'iPad6,3',
    'iPad6,4',
    'iPad6,7',
    'iPad6,8',
    'iPad6,11',
    'iPad6,12'
]
"""


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

    for item in removeFiles:
        if os.path.isfile(item):
            os.remove(item)

    utils.clean()

    argv = sys.argv

    text = 'PyBoot - A tool for tether booting Checkm8 vulnerable iOS devices by Matty, @mosk_i.'
    parser = argparse.ArgumentParser(description=text, usage=f"pyboot -i 'iOS version'\n\nE.G './pyboot -i iPhone9,2 13.2.3 -b ~/Downloads/bootlogo.png'\n\nCurrent PyBoot version is: {tool_version}")
    parser.add_argument("-i", "--ios", help="iOS version you wish to boot", nargs=2, metavar=('DEVICE', 'iOS'))
    parser.add_argument("-b", "--bootlogo", help="Path to .PNG you wish to use as a custom Boot Logo (Must be a .png file with the correct resolution/aspect ratio)", nargs=1, metavar=("LOGO"))
    parser.add_argument('-p', '--pwn', help='Enter PWNDFU mode, which will also apply signature patches', action='store_true')
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

    """
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
    """

    if args.credits:
        print('\033[95m' + "\nCreated by: Matty - @mosk_i\n" + '\033[0m')
        print('\033[94m' + "Other parts by -\n" + '\033[0m')
        print('\033[92m' + "Thimstar - [img4tool]")
        print("realnp - [ibootim]")
        print("axi0mX - [ipwndfu/checkm8]")
        print("Marco Grassi - [PartialZip]")
        print("Merculous - [ios-python-tools]")
        print("0x7ff - [Eclipsa]")
        print("libimobiledevice team - [irecovery]\n" + '\033[0m')
        sys.exit()
    elif args.pwn:
        pwn.pwndfumode()
        exit(22)

    elif args.ios:
        """
        bootchainVariants = {  # iBoot64Patcher doesn't work for iOS 13 iBSS/iBEC so we have to get 12.x iBSS/iBEC to use for booting, but still grab kernel/trustcache (If needed)/devicetree for downgraded iOS version
            'iPhone8,1': '12.4',
            'iPhone8,2': '13.1.3',  # This device has NO keys for 11.x/12.x but i'll keep it here for when it does
            'iPhone9,1': '12.4',
            'iPhone9,2': '12.3.1',
            'iPhone9,3': '12.3.1',
            'iPhone9,4': '12.3.1',
            'iPhone10,3': '12.4',
            'iPhone10,6': '12.4',
            'iPod7,1': '12.3.1',
            'iPad7,5': '12.3.1',
            'iPad7,6': '12.3.1',
            'iPhone6,2': argv[3],  # Since these have all keys up, we can just use whatever the downgraded version is =)
            'iPhone6,1': argv[3],
            'iPhone7,2': argv[3],
            'iPhone7,1': argv[3]  # This device has NO keys for 11.x/12.x but i'll keep it here for when it does
        }
        """
        pass

        if args.bootlogo:
            useCustomLogo = True
            logopath = argv[5]
        else:
            useCustomLogo = False
            logopath = "null"

        print('\033[95m' + "PyBoot - A tool for tether booting Checkm8 vulnerable iOS devices by Matty, @mosk_i\n" + '\033[0m')
        print("Current version is: " + tool_version)

        if "10." in argv[3]:
            print("\nWARNING - 10.x Currently WILL NOT BOOT. You can try if you want to but expect it not to boot!\nPress enter to continue or type anything else and press enter to exit")
            choice = input("")
            if choice == "":
                pass
            else:
                print("Exiting...")
                exit(2)

        print("Make sure your device is connected in DFU mode")
        time.sleep(5)
        img4.img4stuff(argv[2], argv[3], useCustomLogo, logopath)

        # now to pwn device
        print("Exploiting device with checkm8")
        pwn.pwndfumode()

        # Send files to device and boot =)
        img4.sendImages(argv[3], useCustomLogo)

        print("Device should be booting!")
        exit(2)

    elif args.version:
        sys.exit(f"Current version is: {tool_version}")

    else:
        sys.exit(parser.print_help(sys.stderr))


if __name__ == "__main__":
    main()
