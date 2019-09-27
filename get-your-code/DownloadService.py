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

        downloaderObj = cls.getDownloader(siteNum)
        downloaderObj.downloadAllSolutions()


