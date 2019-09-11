import os
import json
import urllib2
import traceback
from BeautifulSoup import BeautifulSoup
from getpass import getpass
from HTMLParser import HTMLParser
from SiteDownloader import SiteDownloader

debug = 0
contestNameDict = {}

class CodeforcesDownloder(SiteDownloader):

    def verifyCredentials(self, username):
        url = "https://codeforces.com/api/user.info?handles=" + str(username)
        resp = urllib2.urlopen(url).read()
        j = json.loads(resp)
        if str(j["status"]) == "FAILED":
            raise Exception("Username does not exists")


    def getContestName(self, contestId):
        # Check in cache
        if contestNameDict.get(contestId) != None:
            return contestNameDict.get(contestId)
        
        url = "http://codeforces.com/contest/" + str(contestId)
        
        # Open the contest page
        resp = urllib2.urlopen(url)
        html = BeautifulSoup(resp)
        
        # get contest Name from contest page
        contestNameTable = html.body.find('table', attrs={'class':'rtable '})
        contestName = contestNameTable.find('th', attrs={'class':'left'}).text
        
        # store the name in cache to avoid re-calculation for same contest-Id
        contestNameDict[str(contestId)] = str(contestName)

        return str(contestName)


    def getFileExtension(self, language):
        
        if "C++" in language:
            return "cpp"
        
        if "Java" in language:
            return "java"
        
        if "GCC" in language:
            return "c"
        
        if "Python" in language:
            return "py"

        #default
        return "txt"


    def downloadFile(self, row, code_directory):
        
        # Extract different parameter from the row
        # print(row)
        contestId = str(row["problem"]["contestId"])
        problemIndex = str(row["problem"]["index"])
        submissionId = str(row["id"])
        problemName = str(row["problem"]["name"].encode("utf-8")).replace(" ", "-")
        submissionLanguage = row["programmingLanguage"]
        contestName = self.getContestName(contestId)

        # print(contestId + " " + submissionId)
        # open submission page for the submission Id
        url = "http://codeforces.com/contest/"+str(contestId)+"/submission/"+str(submissionId)
        resp = urllib2.urlopen(url)
        html = BeautifulSoup(resp)
        
        print("Problem: " + str(contestName) + "-" + str(problemName))
        # Extract the source code
        sourceCodeDiv = html.body.find('pre', attrs={'id':'program-source-text'})
        
        # Convert html entities to human readable format
        # e.g.: &lt -> <, &gt -> > 
        h = HTMLParser()
        code = h.unescape(str(sourceCodeDiv.text))
        
        if debug==1:
            print("Problem: " + str(contestId) + "-" + str(problemName))
        
        # Create folder according to contest name
        save_directory = code_directory + os.path.sep + str(contestName)
        if not os.path.exists(save_directory):
            os.mkdir(save_directory)
        # Save the source code in file
        filename = save_directory + os.path.sep +  problemIndex + "-" + problemName + "." + self.getFileExtension(submissionLanguage)
        if debug==1:
            print("Problem: " + str(contestId) + "-" + str(problemName))
        with open(filename, "w+") as f:
            f.write(str(code))
        if debug==1:
            print("Problem: " + str(contestId) + "-" + str(problemName))
        return


    def getAllAcceptedSubmissions(self, username):

        url = "https://codeforces.com/api/user.status?handle="+ str(username) + "&from=1"
        # print(url)
        resp = urllib2.urlopen(url).read()
        resp = json.loads(resp)
        rows = resp["result"]
        ans = []
        myDict = {}
        for row in rows:
            if str(row["verdict"]) == "OK":
                # Create unique Id for the problem using contest Id and problem index
                problemId = str(row["problem"]["contestId"]) + "-" + str(row["problem"]["index"])
                submissionTime = str(row["creationTimeSeconds"])
                # Check for duplicate and return only latest accepted submission for each problem
                if myDict.get(problemId) == None or str(myDict.get(problemId)["creationTimeSeconds"]) < submissionTime:
                    myDict[problemId] = row
        
        for key, value in myDict.items():
            ans.append(value)
        
        if len(ans) == 0:
            raise Exception("No accepted solutions exist for this user")
        
        return ans



    def downloadAllSolutions(self):
        try:
            username = raw_input("Enter username: ")

            # Check if given username is correct 
            self.verifyCredentials(username)

            directory_name = raw_input("Enter Directory Name: ")
            if not directory_name:
                directory_name = "Codeforces-" + str(username)
            
            code_directory = os.getcwd() + os.path.sep + directory_name
            # Create directory if it's not there
            if not os.path.exists(code_directory):
                os.mkdir(code_directory)
            
            # Get all accepted submissions of the user
            rows = self.getAllAcceptedSubmissions(username)

            # Iterate through all submission and download source-code for them
            for row in rows:
                self.downloadFile(row, code_directory)

        except Exception as e:
            print(e)


