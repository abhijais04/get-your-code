from SpojDownloader import SpojDownloader
from CodeforcesDownloader import CodeforcesDownloder

class DownloadService():

    @classmethod
    def getDownloader(cls, siteNum):
        if siteNum == 1:
            return CodeforcesDownloder()
        elif siteNum == 2:
            return SpojDownloader()
    

    @classmethod
    def downloadSolutions(cls, siteNum):
        # Get a downloader object of the required website
        downloaderObj = cls.getDownloader(siteNum)

        # Download all solutions
        downloaderObj.downloadAllSolutions()


