from SpojDownloader import SpojDownloader
from CodeforcesDownloader import CodeforcesDownloder

def main():

    while True:
        
        print("Enter from following options: ")
        print("1 for Codeforces")
        print("2 for Spoj")

        opt = int(raw_input())
        
        if opt == 1:

            cfd = CodeforcesDownloder()
            cfd.downloadAllSolutions()
            
        elif opt == 2:
            spjd = SpojDownloader()
            spjd.downloadAllSolutions()
        
        else:
            print("Invalid Option !!!")

if __name__ == "__main__":
    main()