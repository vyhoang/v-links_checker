# ________________________________________________________________________  #
# Written by: Vy Hoang                                                      #
# Program: Link Checker - Use requests, chrome driver settings              #
# This program demonstrates link verification and saving bad links          #
# to the report as csv file.                                                #
# ________________________________________________________________________  #

import re
import undetected_chromedriver as uc
import requests
import csv


# chrome driver settings
uc.TARGET_VERSION = 87
options = uc.ChromeOptions()
options.headless = True
options.add_argument('--headless')


class LinkChecker:
    def __init__(self):
        self.badLinks = []

    def crawlURL(self, url):
        """Get all the links inside the page at url"""
        self.badLinks = []
        print("\nStart crawling the url " + url)

        matcher = re.match(r"^(http(s)?://[\w+.]+/)", url)
        base_url = matcher.group()

        # init chrome driver
        driver = uc.Chrome(options=options)
        # open url
        driver.get(url)
        # get all 'a' elements
        a_elements = driver.find_elements_by_css_selector('a')

        checked_urls = []
        # loop thru all links to check if they are valid
        for elem in a_elements:
            # get the url of 'a' element
            link = None
            try:
                link = str(elem.get_attribute('href'))
                if link.startswith("/"):
                    link = link[1:]
                if not link.startswith("http"):
                    link = base_url + link
            except Exception:
                print("\nFailed to get href of the a element ")
            # if url is not already checked else ignore
            if link is not None and not (link in checked_urls):
                # mark url checked to ignore if see it again
                checked_urls.append(link)
                (isValid, code) = self.isValid(link)
                # if link is bad then save it to list of badlinks
                if not isValid:
                    self.badLinks.append({"url": link, "code": code})
        # close chromedriver when no longer use it
        driver.close()

    def isValid(self, link):
        """Check if link is reachable, http status 200, 201, 202"""
        print(".", end="")
        # open http request to link (url)
        try:
            res = requests.head(link)
            res.raise_for_status()
        except Exception as ex:
            print("\nInvalid url format " + link)
            return False, 400

        # if status_code is not 200, 201, 202 then it is not valid
        valid = (res.status_code < 400)
        # return status and the code
        return valid, res.status_code

    def hasBadLinks(self):
        return len(self.badLinks) > 0

    def reportBadLinks(self, file):

        fp = open(file, 'w', newline='')
        # csv headers
        headers = ["Bad Link", "Http Code"]
        csvWriter = csv.DictWriter(fp, headers)
        csvWriter.writeheader()
        print(headers)
        for link_state in self.badLinks:
            csvWriter.writerow({"Bad Link": link_state["url"], "Http Code": link_state["code"]})
            print(link_state["code"], " ", link_state["url"])
        print("\nReport was saved at " + file)


def main():

    # Input url or take the default url
    url = input("\nEnter an url (default=https://docs.python.org/3/): ")\
          or "https://docs.python.org/3/"
    checker = LinkChecker()
    # search all urls in the page
    checker.crawlURL(url)

    if checker.hasBadLinks():
        # name of report file or default file
        file = input("\nEnter a csv filename to save the report (default=report.csv):\n") \
               or "report.csv"
        # save report
        checker.reportBadLinks(file)
    else:
        print("\nNo bad links found.")


if __name__ == '__main__':
    main()
