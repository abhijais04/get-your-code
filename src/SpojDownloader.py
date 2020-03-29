import os
from mechanize import Browser
import urllib2
import traceback
from BeautifulSoup import BeautifulSoup
from getpass import getpass
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class SpojDownloader():
    
    def verifyCredentials(self, resp):
        """Verifies credentials for user
        Checks if the response is proper 
        raises Exception if username or password is wrong
        """

        logging.info("Verifying credentials")
        if "Authentication failed" in str(resp):
            raise Exception("Login Failed")
        logging.info("Login successfull")

    
    def login(self, url, username, password):
        """ Login in the given url with given username and password
        returns a browser instance which has an active logged in sesssion
        raises exception if any error occurs, or if credentials are wrong
        """

        logging.info("Logging in with the given credentials")
        try:
            # Create a browser instance
            b = Browser()
            b.open(url)
            b.select_form(nr=0)
            
            # Enter the username password
            b["login_user"] = username
            b["password"] = password

            # Login with given credentials
            b.submit()
            response = b.response().read()
            self.verifyCredentials(response)
        except Exception as e:
            logging.error(e)
            raise Exception("Login Failed: Invalid Credentials")
        return b

    
    def downloadFile(self, br, siteUrl, fileName):
        """ Downlaod source code file in local directory 
        raise Exception if error occurs
        """
        problemName = os.path.basename(fileName)
        problemName = problemName.split('.')[0]
        logging.info("Problem :" + str(problemName))
        logging.info("Downloading source code from:" + siteUrl + "into file:" + fileName)
        try:
            br.retrieve(siteUrl,fileName)[0]
        except Exception as e:
            logging.error("Error while downloading file !!")
            logging.error(traceback.print_exc())
            raise e
        logging.info("Download successfull")

    
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
        """ Get all solved problems solved by user
        return a list of unique problem-codes for all solved problems
        """

        logging.info("Getting list of solved problems by user")
        
        # Profile page for Spoj.com
        # https://www.spoj.com/users/{usrename}
        profileUrl = baseurl + "/users/" + username + "/"
        try:
            # Open profile page
            response = urllib2.urlopen(profileUrl)
            html = response.read()
            
            # create parse tree of response
            html = BeautifulSoup(html)
            
            # Use parse tree for finding desired information 
            solvedProblemsTable = html.body.find('table', attrs={'class':'table table-condensed'})
            all_tags = solvedProblemsTable.findAll('a', href=True)
            all_links = [a.get('href') for a in all_tags]
            
            # extract problem codes from /status/problem_code, username/
            all_codes = [str(s.split('/')[2].split(',')[0]) for s in all_links]
            
        except Exception as e:
            logging.error("Error while getting solved problem list")
            raise e
        
        if len(all_codes) < 1:
            raise Exception("No Solved problem found for this user")
        
        logging.info("Number of solved problems: " + str(len(all_codes)))

        return all_codes


    def getDownloadLinkForProblem(self, baseurl, br , username, problemCode):
        """ Fetch download link for a given problem link
        returns url to download the file
        also returns the extension for file e.g: ".cpp", ".java"
        """
        try:
            # Get ueer's submission history for problem 
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
                # Save the submission_id if the solution was correct
                if status == "accepted":
                    res = "https://www.spoj.com/files/src/save/" + id + "/"
                    extension = self.getExtension(lang)
                    break
            if res == None:
                raise Exception("Accepted solution not found for code: " + str(problemCode))
            
        except Exception as e:
            logging.error("Error while getting download link for " + problemCode)
            raise e
        return res, extension


    def downloadAllSolutions(self):
        """ Get username, password as input
        downlaods source code for all the solved problems by user
        """

        try:
            baseurl = "https://www.spoj.com"
            # Get username password
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
                    link, extension = self.getDownloadLinkForProblem(baseurl, br, username, code)
                    filename = save_directory + os.path.sep + code + extension
                    self.downloadFile(br, link, filename)
                except:
                    print("Could not download for code : " + str(code))
        except Exception as e:
            print(e)
