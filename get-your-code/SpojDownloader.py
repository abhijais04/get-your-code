import os
from mechanize import Browser
import urllib2
import traceback
from BeautifulSoup import BeautifulSoup
from getpass import getpass
from SiteDownloader import SiteDownloader


class SpojDownloader(SiteDownloader):
    def verifyCredentials(self, resp):
        if "Authentication failed" in str(resp):
            raise Exception("Login Failed")
        return 

    def login(self, url, username, password):
        try:
            b = Browser()
            b.open(url)
            b.select_form(nr=0)
            b["login_user"] = username
            b["password"] = password
            b.submit()
            response = b.response().read()
            self.verifyCredentials(response)
        except:
            # print(e)
            traceback.print_exc()
            raise 
        return b

    def downloadFile(self, br, siteUrl, filename):

        try:
            br.retrieve(siteUrl,filename)[0]
        except:
            print("Error while downloading file !!")
            traceback.print_exc()
            raise

    def printObject(self, obj):
        for att in dir(obj):
            print (att, getattr(obj,att))

    def getExtension(self, lang):
        if "cpp" in lang or "CPP" in lang:
            return ".cpp"
        if "java" in lang or "JAVA" in lang:
            return ".java"
        if "py" in lang or "PY" in lang:
            return ".py"
        if lang == "c" or lang == "C":
            return ".c"
        return ".txt"

    def getSolvedProblemLinksOfUser(self, baseurl, username):
        # Profile page for Spoj.com
        # https://www.spoj.com/users/{usrename}
        profileUrl = baseurl + "/users/" + username + "/"
        response = urllib2.urlopen(profileUrl)
        html = response.read()
        html = BeautifulSoup(html)
        solvedProblemsTable = html.body.find('table', attrs={'class':'table table-condensed'})
        all_tags = solvedProblemsTable.findAll('a', href=True)
        all_links = [a.get('href') for a in all_tags]
        
        # extracting problem codes from /status/problem_code, username/
        all_codes = [str(s.split('/')[2].split(',')[0]) for s in all_links]
        if len(all_codes) < 1:
            raise Exception("No Solved problem found for this user")
        return all_codes


    def getDownloadLinkForProblem(self, baseurl, br , username, problemCode):
        
        try:
            url = baseurl + "/status/" + str(problemCode) + "," + str(username) + "/"
            html = br.open(url).read()
            html = BeautifulSoup(html)
            problemStatusTable = html.body.find('table', attrs={'class':'problems table newstatus'})
            rows = problemStatusTable.find('tbody').findAll('tr')
            res = None
            extension = None
            for row in rows:
                status = row.find('td', attrs={'class':'statusres text-center'}).findAll("strong")[0].text
                id = row.find('td', attrs={'class':'statustext text-center'}).find('a').text
                lang = row.find('td', attrs={'class':'slang text-center'}).text
                if status == "accepted":
                    res = "https://www.spoj.com/files/src/save/" + id + "/"
                    extension = self.getExtension(lang)
                    break
            if res == None:
                raise Exception("Accepted solution not found for code: " + str(problemCode))
            
        except:
            raise
        return res, extension


    def downloadAllSolutions(self):
        baseurl = "https://www.spoj.com"
        username = raw_input("Enter usrename: ")
        password = getpass()
            
        # login with given usrname and password
        br = self.login(baseurl, username, password)

        # get list of all solved problems for the given user
        solvedProblemList = self.getSolvedProblemLinksOfUser(baseurl, username)

        # Path to save the code
        save_directory = os.getcwd() + os.path.sep  + "Spoj"
        # Create directory if it's not there
        if not os.path.exists(save_directory):
            os.mkdir(save_directory)
        
        # download solution for each problem code
        counter = 0 
        total = len(solvedProblemList)
        for code in solvedProblemList:
            counter += 1
            print("Downloading " + str(counter) + "/" + str(total))   
            try:
                link, extension = getDownloadLinkForProblem(baseurl, br, username, code)
                filename = save_directory + os.path.sep + code + extension
                downloadFile(br, link, filename)
            except:
                print("Could not download for code : " + str(code))

