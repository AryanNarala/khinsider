import requests
from bs4 import BeautifulSoup
import jsbeautifier
from urllib.parse import unquote
import sys
import os

MAIN_URL = "https://downloads.khinsider.com/"
DOWNLOAD_URL = "https://vgmsite.com/soundtracks/"


class Album:
    def __init__(self, url):
        self.name = url
        self.albumURL = MAIN_URL + "game-soundtracks/album/" + url
        self.tracks = []

    def parsePage(self):
        html = requests.get(self.albumURL).text
        soup = BeautifulSoup(html, "html.parser")

        formatSegment = soup.find_all(id="songlist_header")

        bad = ["#", "Song Name", "CD"]
        formats = []

        for item in formatSegment[0].find_all("b"):
            if item.getText() not in bad:
                formats.append(item.getText())

        scriptSegment = soup.find_all("script")

        packedCode = str(scriptSegment[3])
        unpackedCode = jsbeautifier.beautify(packedCode)

        tracksData = eval(unpackedCode.split("tracks = ")[1].split(",\n            trackCount")[0])

        self.addTracks(tracksData)

    def addTracks(self, tracksData):
        for trackData in tracksData:
            trackData["album"] = self.name
            self.addTrack(trackData)

    def addTrack(self, trackData):
        self.tracks.append(Track(trackData))

    def download(self, verbose=True):
        if verbose:
            print("Downloading Album: " + self.name + "\n")

        self.parsePage()

        if not os.path.exists(self.name):
            os.mkdir(self.name)

        for track in self.tracks:
            track.download()


class Track:
    def __init__(self, trackData):
        self.album = trackData["album"]
        self.number = trackData["track"]
        self.name = trackData["name"]
        self.url = DOWNLOAD_URL + self.album + "/" + trackData["file"]
        self.file = unquote(trackData["file"]).split("/")[1]

    def download(self, path=None, verbose=True):
        if verbose:
            print("Downloading Track: " + self.name)

        response = requests.get(self.url)
        with open(self.album + "/" + self.file, "wb") as file:
            file.write(response.content)
            file.close()


def searchAlbum(term):
    html = requests.get("https://downloads.khinsider.com/search", params={"search": term}).text
    soup = BeautifulSoup(html, "html.parser")

    results = soup.find(id="EchoTopic")

    albumResults = []

    for track in results.find_all("a"):
        albumResults.append(Album("https://downloads.khinsider.com" + track["href"]))

    for album in albumResults:
        print(album.name)


def downloadAlbum(albumURL):
    album = Album(albumURL)
    album.download()


if __name__ == '__main__':
    link = sys.argv[1].split("/")[-1]
    downloadAlbum(link)
