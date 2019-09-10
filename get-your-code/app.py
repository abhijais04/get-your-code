import SpojDownloader
import CodeforcesDownloader

def main():

    while True:
        
        print("Enter from following options: ")
        print("1 for Codeforces")
        print("2 for Spoj")

        opt = int(raw_input())

        if opt == 1:
            CodeforcesDownloader.downloadAllSolutions()
        elif opt == 2:
            SpojDownloader.downloadAllSolutions()
        else:
            print("Invalid Option !!!")
        