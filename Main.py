import requests #handles get requests
from bs4 import BeautifulSoup #nice wrapper package for html exploration
import csv #used to write to output file
import os #used for checking/making file paths
import sys #used for progress bar printing


#class that contains all the scraping methods and results
class WebScraper:
    def __init__(self, webTarget=None):
        self.scrapes = dict() #where results of scrapes are stored
        self.webTarget = webTarget #the website to scrape

    def getScrapes(self):
        return self.scrapes

    def setTarget(self, newTarget):
        self.webTarget = newTarget

    #tries a single get request to a website
    def tryScrape(self):
        try:
            return requests.get(self.webTarget)
        except Exception as e:
            print("ERROR: {exception}".format(exception=e))
            return None

    #parses results of a scrape, can be static because it never references 'self'
    @staticmethod
    def parseResponse(resp):
        soup = BeautifulSoup(resp.content, 'html.parser')
        attributes = soup.find_all('li')
        name, purpose = None, None
        for attr in attributes:
            if "Name:" in attr.text:
                name = attr.text.split("Name: ")[1]
            elif "Purpose:" in attr.text:
                purpose = attr.text.split("Purpose: ")[1]

        return name, purpose

    #writes scrape results to a csv file
    def exportResults(self):
        if not bool(self.scrapes): #checks to see if scrapes exists before exporting
            print("Warning: no scrapes found, is target website correct?")
        else:
            if not os.path.isdir("Output"): #checks/makes output folder
                os.mkdir("Output")

            writer = csv.writer(open("Output/scrapes.csv", "w", newline=""))
            writer.writerow(["NAME", "PURPOSE"]) #column names
            for key, val in self.scrapes.items(): #loop through results and write each one to a new line
                writer.writerow([key, val])

    #tries to make calls to the target website
    def runScrapes(self,
                   numScrapes=50, #number of times to scrape the target site
                   quitThreshold = None, #number of failed scrapes before quitting
                   verbose=True): #print progress bar to console?
        quitThreshold = numScrapes * 4 if quitThreshold is None else quitThreshold
        successfulScrapes = 0
        failedScrapes = 0

        while successfulScrapes < numScrapes:
            resp = self.tryScrape() #make the get request
            if resp is not None: #did the request work?
                if verbose: #prints scrape progress to screen
                    sys.stdout.write("\rScraping: {:.1f}%".format((successfulScrapes + 1) / numScrapes * 100))
                    if successfulScrapes == numScrapes - 1:
                        print("")

                name, purpose = self.parseResponse(resp) #finds name and purpose information in the html
                if name is not None and purpose is not None: #did it find those results?
                    successfulScrapes += 1
                    self.scrapes[name] = purpose
                else:
                    failedScrapes += 1
            else:
                failedScrapes += 1

            if failedScrapes == quitThreshold:
                print("ERROR: TOO MANY FAILED SCRAPES, QUITTING")
                break

#run the assignment
def main():
    webTarget = 'http://3.95.249.159:8000/random_company'
    scraper = WebScraper(webTarget) #create the scraper
    scraper.runScrapes()
    scraper.exportResults()

if __name__ == "__main__":
    main()
