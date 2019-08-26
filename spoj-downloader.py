'''
To-do
    Add login check
    make extensible using design pattern
    add progress bar
'''

import os
from mechanize import Browser
import urllib2
import traceback
from BeautifulSoup import BeautifulSoup
from getpass import getpass


def login(url, username, password):
    try:
        b = Browser()
        b.open(url)
        b.select_form(nr=0)
        b["login_user"] = username
        b["password"] = password
        b.submit()
        response = b.response().read()
        if username in response:
            print("Logged in!")
    except:
        print("Error while logging in !!! ")
        traceback.print_exc()
        raise
    return b

def downloadFile(br, siteUrl, filename):

    try:
        br.retrieve(siteUrl,filename)[0]
    except:
        print("Error while downloading file !!")
        traceback.print_exc()
        raise

def printObject(obj):
    for att in dir(obj):
        print (att, getattr(obj,att))


def getSolvedProblemLinksOfUser(baseurl, username):
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
    return all_codes


def getDownloadLinkForProblem(baseurl, br , username, problemCode):

    url = baseurl + "/status/" + str(problemCode) + "," + str(username) + "/"
    html = br.open(url).read()
    html = BeautifulSoup(html)
    problemStatusTable = html.body.find('table', attrs={'class':'problems table newstatus'})
    rows = problemStatusTable.find('tbody').findAll('tr')
    res = None
    for row in rows:
        status = row.find('td', attrs={'class':'statusres text-center'}).findAll("strong")[0].text
        id = row.find('td', attrs={'class':'statustext text-center'}).find('a').text
        if status == "accepted":
            res = "https://www.spoj.com/files/src/save/" + id + "/"
            break
    
    # print(res)
    return res


def downloadAllSolutions():
    baseurl = "https://www.spoj.com"
    username = raw_input("Enter usrename: ")
    password = getpass()
    save_directory = str(os.getcwd()) + os.path.sep + "Spoj"

    # Create directory if it's not there
    if not os.path.exists(save_directory):
        os.mkdir(save_directory)
    
    try:
        # login with given usrname and password
        br = login(baseurl, username, password)
    except:
        print("Login failed !!!!! ")
        return 

    # get list of all solved problems for the given user
    solvedProblemList = getSolvedProblemLinksOfUser(baseurl, username)

    # download solution for each of them
    counter = 0 
    total = len(solvedProblemList)
    for code in solvedProblemList:
        counter += 1
        print("Downloading " + str(counter) + "/" + str(total))
        
        try:
            link = getDownloadLinkForProblem(baseurl, br, username, code)
            filename = save_directory + os.path.sep + code + ".cpp"
            downloadFile(br, link, filename)
        except:
            print("Could not download for code : " + str(code))


downloadAllSolutions()