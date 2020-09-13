import os
import json
from urllib.request import urlopen
import traceback
from bs4 import BeautifulSoup
from getpass import getpass
from html.parser import HTMLParser
import logging
import requests

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class CodeforcesDownloder():

    # A cache to avoid re-calling same http request for fetching same info
    contestNameCache = {}

    def __init__(self): 
        self.contestNameDict = self.contestNameCache
    

    # Method for verifying user credentials
    # Raises exception if the username is not valid
    def verifyCredentials(self, username):    
        logging.info("Verifying username: " + username)

        # Codeforces API url
        url = "https://codeforces.com/api/user.info?handles=" + str(username)
        
        try:
            # Send http request at the url
            resp = requests.get(url)
            
            # Api will return status_Code as 400 in case of wrong username
            if resp.status_code == 400:
                logging.error("Username "+ str(username) +" does not exists")
                raise Exception("Invalid Credentials")
            
            # Catch all other HTTP connection error
            if resp.status_code != 200:
                logging.error("HTTP Error while verifying credentials, returned status code: " + str(resp.status_code))
                raise Exception("HTTP Error " + str(resp.status_code))
            
        except Exception as e:
            raise
        
        logging.info("Username is Valid")
    

    # Gets contest Name for a given contest ID
    def getContestName(self, contestId):
        
        # Check in cache
        if self.contestNameDict.get(contestId) != None:
            return self.contestNameDict.get(contestId)
        
        url = "http://codeforces.com/contest/" + str(contestId)
        
        # Open the contest page
        resp = urlopen(url).read()
        html = BeautifulSoup(resp, "html.parser")
        
        # get contest Name from contest page
        contestNameTable = html.body.find('table', attrs={'class':'rtable'})
        contestName = contestNameTable.find('th', attrs={'class':'left'}).text
        
        # store the name in cache to avoid re-calculation for same contest-Id
        self.contestNameDict[str(contestId)] = str(contestName)

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


    # Downloads the source code for a problem in the given directory
    # row: Dict with all info about the problem
    def downloadFile(self, row, code_directory):
        
        try:
            # Extract different parameter from the row
            contestId = str(row["problem"]["contestId"])
            problemIndex = str(row["problem"]["index"])
            submissionId = str(row["id"])
            problemName = str(row["problem"]["name"]).replace(" ", "-")
            submissionLanguage = row["programmingLanguage"]
            contestName = self.getContestName(contestId)

            # open submission page for the submission Id
            url = "http://codeforces.com/contest/"+str(contestId)+"/submission/"+str(submissionId)
            resp = urlopen(url)
            html = BeautifulSoup(resp, "html.parser")
            
            logging.info("Problem: " + str(contestName) + "-" + str(problemName))
            # Extract the source code
            sourceCodeDiv = html.body.find('pre', attrs={'id':'program-source-text'})
            
            # Convert html entities to human readable format
            # e.g.: "&lt" becomes "<", "&gt" becomes ">" 
            h = HTMLParser()
            code = h.unescape(str(sourceCodeDiv.text))
            
            # Create folder according to contest name
            save_directory = code_directory + os.path.sep + str(contestName)

            if not os.path.exists(save_directory):
                logging.info("Creating Directory: " + save_directory)
                os.mkdir(save_directory)
                
            # Save the source code in file
            filename = save_directory + os.path.sep +  problemIndex + "-" + problemName+ "." + self.getFileExtension(submissionLanguage)
            logging.info("Saving Source code in file:" + str(os.path.basename(filename)))
            with open(filename, "w+") as f:
                f.write(str(code))
        except Exception as e:
            logging.info("Error while downloading file !!!")
            raise

        return

    # Get list of all solved problems by user
    def getAllAcceptedSubmissions(self, username):

        url = "https://codeforces.com/api/user.status?handle="+ str(username) + "&from=1"
        logging.info("Getting list of all solved problems...")
        try:
            resp = urlopen(url).read()
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
            
            # Store All the solved problems in a list
            for key, value in myDict.items():
                ans.append(value)
            
            logging.info("Number of solved questions: " + str(len(ans)))
            if len(ans) == 0:
                logging.error("No solved solutions exists for this user")
                raise Exception("No accepted solutions exist for this user")
        except Exception as e:
            logging.error("Error in getAllAcceptedSubmissions method !!!")
            raise
        
        return ans


    # Download all the solutions for given user
    def downloadAllSolutions(self, params):
        
        try:
            username = params.get("username")

            # Check if given username is correct 
            self.verifyCredentials(username)

            directory_name = "codeforces-" + str(username)
            code_directory = os.getcwd() + os.path.sep + directory_name
            
            # Create directory if it's not there
            if not os.path.exists(code_directory):
                logging.info("Creating directory: " + code_directory)
                os.mkdir(code_directory)
            
            # Get all accepted submissions of the user
            rows = self.getAllAcceptedSubmissions(username)


            # Iterate through all submission and download source-code for them
            for row in rows:
                self.downloadFile(row, code_directory)

        except Exception as e:
            print(e)
            raise


