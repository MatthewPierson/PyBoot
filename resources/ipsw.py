import plistlib
import sys
import os
import shutil
from zipfile import ZipFile, is_zipfile

def readmanifest(path, flag):
    fn = path
    with open(fn, 'rb') as f:
        pl = plistlib.load(f)

    if flag:
        result = pl['ProductVersion']
    else:
        supportedModels = str(pl['SupportedProductTypes'])
        supportedModels1 = supportedModels.replace("[", "")
        supportedModels2 = supportedModels1.replace("'", "")
        result = supportedModels2.replace("]", "")

    return result

def unzipIPSW(path):
    if is_zipfile(path): # First of all, check to see if fname is an actual ipsw, by verifying the file is a zip archive (ipsw's are just zip files).
        print(f'{path} is a zip archive!')
    else:
        sys.exit(f'"{path}" is not a zip archive! Are you sure you inserted the correct ipsw path?')
    
    print("Starting IPSW unzipping")
    outputFolder = "IPSW"
    newpath = path.rstrip()
    fname = str(newpath)
    testFile = os.path.exists(fname)

    if os.path.exists('IPSW'):
        shutil.rmtree('IPSW')
        os.mkdir('IPSW')
    elif not os.path.exists('IPSW'):
        os.mkdir('IPSW')

    while not testFile or not fname.endswith!=(".ipsw"):
        print("Invalid filepath/filename.\nPlease try again with a valid filepath/filename.")
        fname = input("Enter the path to the IPSW file (Or drag and drop the IPSW into this window):\n")
        newpath = fname.rstrip()
        fname = str(newpath)
        testFile = os.path.exists(fname)

    if testFile and fname.endswith(".ipsw"):

        print("IPSW found at given path...")
        print("Cleaning up old files...")
        shutil.rmtree("IPSW")
        print("Unzipping..")

        with ZipFile(fname, 'r') as zip_ref:
            zip_ref.extractall(outputFolder)
        source = ("IPSW/Firmware/dfu/")
        dest1 = os.getcwd()

        files = os.listdir(source)

        for f in files:
            shutil.move(source + f, dest1 + "/IPSW/")
