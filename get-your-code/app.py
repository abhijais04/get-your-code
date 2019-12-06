from DownloadService import DownloadService
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def main():

    while True:
        
        print("Enter from following options: ")
        print("1 for Codeforces")
        print("2 for Spoj")
        
        try:
            opt = int(raw_input())
        except ValueError as e:
            logging.error(e)
            print("Don't try anything studpid :) ")
            continue
        
        if opt > 2 or opt < 1:
            logging.info("Wrong option selected!!")
            print("You should read the options first :) ")
            continue
        
        DownloadService.downloadSolutions(opt)
        

if __name__ == "__main__":
    main()