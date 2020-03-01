import json
import os
import shutil
from urllib.request import urlretrieve

from remotezip import RemoteZip

from resources.iospythontools.utils import (downloadJSONData, progress,
                                            splitToFileName)


"""

This is mainly the heart of the script.

Handles data from ipsw.me api

"""


class APIParser(object):
    def __init__(self, device, version, beta=False):
        super().__init__()
        self.device = device
        self.version = version

    def linksForDevice(self, filetype):
        url = f'https://api.ipsw.me/v4/device/{self.device}?type={filetype}'
        return downloadJSONData(url, self.device)

    def iOSToBuildid(self):
        self.linksForDevice('ipsw')
        with open(f'{self.device}.json', 'r') as file:
            data = json.load(file)
            i = 0
            iOSFromJsonFile = data['firmwares'][i]['version']
            while iOSFromJsonFile != self.version:
                i += 1
                iOSFromJsonFile = data['firmwares'][i]['version']

            buildid = data['firmwares'][i]['buildid']

        file.close()
        return buildid

    def downloadIPSW(self):
        buildid = self.iOSToBuildid()
        self.linksForDevice('ipsw')
        with open(f'{self.device}.json', 'r') as file:
            data = json.load(file)
            i = 0
            buildidFromJsonFile = data['firmwares'][i]['buildid']
            while buildidFromJsonFile != buildid:
                i += 1
                buildidFromJsonFile = data['firmwares'][i]['buildid']

            url = data['firmwares'][i]['url']
            ios = data['firmwares'][i]['version']
            filename = splitToFileName(url)

            print('Device:', self.device)
            print('iOS:', ios)
            print('Buildid:', buildidFromJsonFile)
            print('Filename:', filename)
            urlretrieve(url, filename, progress)
            print('\n')
        file.close()

    def signed(self):
        signedVersions = []

        # Get ipsw signed versions

        self.linksForDevice('ipsw')
        with open(f'{self.device}.json', 'r') as file:
            data = json.load(file)
            for stuff in data['firmwares']:
                ios = stuff['version']
                buildid = stuff['buildid']
                status = stuff['signed']
                versions = [ios, buildid, 'ipsw']
                if status:  # If

                    signedVersions.append(versions)
        file.close()

        # Get ota signed versions

        self.linksForDevice('ota')
        with open(f'{self.device}.json', 'r') as f:
            data = json.load(f)
            for stuff in data['firmwares']:
                ios = stuff['version']
                # print(ios[0:3])
                if ios[0:3] == "9.9":  # Beginning with iOS 10, now versions also include 9.9 at the beginning, example, 9.9.10.3.3. Skip these.
                    pass
                else:
                    buildid = stuff['buildid']
                    status = stuff['signed']
                    currentOTA = [ios, buildid, 'ota']

                    if status:  # If signed
                        for build in signedVersions:
                            # print(build)
                            # We may just need to parse the whole list itself, instead of the contents.
                            alreadySigned = build[0]  # prints ios from ipsw
                            OTAsigned = currentOTA[0]  # prints ios from ota
                            if OTAsigned == alreadySigned:  # If the iOS versions are the same FIXME
                                #print("No need to add OTA:", OTAsigned)
                                break
                            else:
                                # CurrentOTA = 9.3.5, ..., 'ota' is not because of 'ota', we need to check if the ios and buildid list is already there
                                if currentOTA not in signedVersions:  # If the iOS, buildid, type is not in signedVersions FIXME
                                    signedVersions.append(currentOTA)  # Add the current ios, buildid, as OTA
                                    # print("adding" + str(currentOTA))  # 9.3.5 ota is being print here

        f.close()

        # TODO Clean up iOS 10 will have 9.9.10.3.3 for example. We need to print versions with unique buildids once, and if ipsw is signed, only print ipsw signed.

        # TODO Printed signed versions for iPhone4,1 still gives 9.3.5 ipsw and ota

        return signedVersions

    def downloadFileFromArchive(self, path, output):
        buildid = self.iOSToBuildid()
        self.linksForDevice('ipsw')
        with open(f'{self.device}.json', 'r') as file:
            data = json.load(file)
            i = 0
            buildidFromJsonFile = data['firmwares'][i]['buildid']
            while buildidFromJsonFile != buildid:
                i += 1
                buildidFromJsonFile = data['firmwares'][i]['buildid']

            url = data['firmwares'][i]['url']
            filename = splitToFileName(url)
            zip = RemoteZip(url)
            print(f"Extracting: {path}, from {filename}")
            zip.extract(path)
            zip.close()

            if output:

                shutil.move(path, output)

        file.close()

    def printURLForArchive(self):
        buildid = self.iOSToBuildid()
        self.linksForDevice('ipsw')
        with open(f'{self.device}.json', 'r') as file:
            data = json.load(file)
            i = 0
            buildidFromJsonFile = data['firmwares'][i]['buildid']
            while buildidFromJsonFile != buildid:
                i += 1
                buildidFromJsonFile = data['firmwares'][i]['buildid']

            url = data['firmwares'][i]['url']

        file.close()
        return url
