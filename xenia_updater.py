import requests
from bs4 import BeautifulSoup as Soup
import os
from dateutil import parser
from zipfile import ZipFile
from argparse import ArgumentParser

CANARY_URL = 'https://github.com/xenia-canary/xenia-canary/releases/latest/'
CANARY_DOWNLOAD = CANARY_URL + 'download/xenia_canary.zip'
MASTER_URL = 'https://github.com/xenia-project/release-builds-windows/releases/latest'
MASTER_DOWNLOAD = MASTER_URL + 'download/xenia_master.zip'


class XeniaBuild:
    def __init__(self, release_page: str, download_url: str, executable: str) -> None:
        self.release_page = release_page
        self.download_url = download_url
        self.executable = executable
        self.zip_name = self.download_url.split('/')[-1]

    def is_newer_build_available(self) -> bool:
        print("Checking for newer builds...")

        # fetch timestamp of latest release
        r = requests.get(self.release_page)
        soup = Soup(r.content, 'lxml')
        time = soup.find('relative-time')['datetime']
        timestamp = parser.isoparse(time).timestamp()

        # check timestamp of existing exe or download if exe is not available
        try:
            cur_timestamp = os.path.getmtime(self.executable)
        except FileNotFoundError:
            return True

        return timestamp > cur_timestamp

    def download_build(self) -> None:
        print("Downloading latest build...")

        # write zip contents as binary
        r = requests.get(self.download_url)
        with open(self.zip_name, 'wb') as f:
            f.write(r.content)

    def unzip(self) -> None:
        print(f"Unzipping {self.zip_name}...")

        # extract all files into current directory and delete zip
        with ZipFile(self.zip_name, 'r') as zf:
            zf.extractall('.')
        os.remove(self.zip_name)


BUILD_TYPES = {
    'canary': XeniaBuild(CANARY_URL, CANARY_DOWNLOAD, 'xenia_canary.exe'),
    'master': XeniaBuild(MASTER_URL, MASTER_DOWNLOAD, 'xenia.exe')
}

if __name__ == '__main__':
    # usage: xenia_updater.py --build {master, canary}
    # takes 'canary' by default
    argparser = ArgumentParser(prog="xenia_updater.py")
    argparser.add_argument(
        '--build',
        choices=['master', 'canary'],
        default='canary'
    )
    args = argparser.parse_args()

    xb = BUILD_TYPES.get(vars(args)['build'])

    if xb.is_newer_build_available():
        xb.download_build()
        xb.unzip()
    else:
        print("Already up to date...")
