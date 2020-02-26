import json
import os
import re

from remotezip import RemoteZip

from resources.iospythontools.ipswapi import APIParser


class Manifest(object):  # TODO Add OTA compatibility
    def __init__(self, device, version):
        super().__init__()
        self.device = device
        self.version = version

    def downloadBuildManifest(self):
        shit = APIParser(self.device, self.version)
        buildid = shit.iOSToBuildid()
        shit.linksForDevice('ipsw')

        with open(f'{self.device}.json', 'r') as file:
            data = json.load(file)
            i = 0
            buildidFromJsonFile = data['firmwares'][i]['buildid']
            while buildidFromJsonFile != buildid:
                i += 1
                buildidFromJsonFile = data['firmwares'][i]['buildid']

            url = data['firmwares'][i]['url']
            manifest = 'BuildManifest.plist'

            # Start the process of reading and extracting a file from a url

            #print(f'Downloading manifest for {self.version}, {buildid}')
            zip = RemoteZip(url)
            zip.extract(manifest)
            # This can be done better
            os.rename(manifest, f'BuildManifest_{self.device}_{self.version}_{buildid}.plist')
            #print('Done downloading!')
            zip.close()

        file.close()

    def manifestParser(self):
        oof = APIParser(self.device, self.version)
        buildid = oof.iOSToBuildid()
        manifest = f'BuildManifest_{self.device}_{self.version}_{buildid}.plist'

        if not os.path.exists(manifest):
            self.downloadBuildManifest()

        with open(manifest, 'r') as f:
            data = f.read().replace('\t', '').splitlines()
        f.close()
        return data

    def getCodename(self):
        api = APIParser(self.device, self.version)
        buildid = api.iOSToBuildid()
        manifest = f'BuildManifest_{self.device}_{self.version}_{buildid}.plist'
        data = self.manifestParser()
        control = data.index('<key>BuildTrain</key>')
        index = control + 1
        codename = re.sub('<[^>]*>', '', data[index])  # Cheeky HTML tag removal :D
        os.remove(manifest)
        return codename

    def getBasebandVersion(self):
        data = self.manifestParser()
        control = data.index('<key>BasebandFirmware</key>')  # 33, wrong, need the second (not particularly bad)
        print(control)
