from SpojDownloader import SpojDownloader
from CodeforcesDownloader import CodeforcesDownloder
from constants import Websites

class DownloadService():

    @classmethod
    def getDownloader(cls, siteNum):
        if Websites(siteNum) == Websites.CODEFORCES:
            return CodeforcesDownloder()
        elif Websites(siteNum) == Websites.SPOJ:
            return SpojDownloader()
    

    @classmethod
    def downloadSolutions(cls, siteNum, params):
        try:
            # Get a downloader object of the required website
            downloaderObj = cls.getDownloader(siteNum)

            # Download all solutions
            downloaderObj.downloadAllSolutions(params)
        except Exception as e:
            print(e)
            raise



