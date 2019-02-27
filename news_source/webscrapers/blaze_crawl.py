import pickle, datetime, re, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib import robotparser

class slate_crawler(object):

    def __init__(self):

        self.driver = webdriver.Chrome()

        self.links = []

        self.data = []

        self.harvest_range = (0, 1)

    def get_driver(self, ua):

        opts = Options()
        opts.add_argument(f"user-agent={ua}")
        to_return = webdriver.Chrome(chrome_options=opts)
        to_return.get("https://www.google.com/")

    def get_links(self):

        start_time = time.time()

        self.driver.get("https://www.theblaze.com/news")

        gathered_links = []
        for i in range(110):
            time.sleep(11)
            try:
                self.driver.find_element_by_xpath("""//*[@id="hbLoadMore"]""").click()
            except Exception:
                print("Sleeping 6 sec. for page to load")
                time.sleep(6)
                try:
                    self.driver.find_element_by_xpath("""//*[@id="hbLoadMore"]""").click()
                except Exception:
                    time.sleep(4)
                    print("Sleeping 4 more for the persistant page...")
                    try:
                        self.driver.find_element_by_xpath("""//*[@id="hbLoadMore"]""").click()
                    except Exception:
                        print("The page won't load! :(")
            if i % 10 ==0:
                print(f"Clicked load more {i} times now")

        time.sleep(15)
        elems = self.driver.find_elements_by_class_name("feed-link")
        for e in elems:
            link = e.get_attribute('href')
            if ".com/glenn-beck" not in link and ".com/doc" not in link and ".com/unleashed" not in link:
                gathered_links.append(link)

        gathered_links = set(gathered_links)

        print(f"Got {len(gathered_links)} links in {time.time() - start_time} seconds")

        self.links = gathered_links


    def get_robo_link(self, link):
        if ".com/" in link:
            robo_link = link.split('com')[0] + "com/robots.txt"
        elif ".org/" in link:
            robo_link = link.split('org')[0] + "org/robots.txt"
        elif ".edu/" in link:
            robo_link = link.split('edu')[0] + "edu/robots.txt"
        else:
            robo_link = ""
        return robo_link

    def check_links(self):

        checked_links = []
        rp = robotparser.RobotFileParser()

        for l in self.links:
            try:
                rp.set_url(self.get_robo_link(l))
                rp.read()
                if rp.can_fetch("*", l):
                    checked_links.append(l)
            except Exception:
                print(f"Failed to check {l}")
        self.links = checked_links


    def get_data(self):

        to_visit = self.links
        data = [[]]*len(to_visit)

        index = 0
        for link in to_visit:

            try:
                self.driver.get(link)

                time.sleep(16)
                end_time = time.time()

                temp_link = link
                temp_title = self.driver.find_element_by_class_name('page-title').text

                article = ""
                text = self.driver.find_element_by_class_name("entry-content")
                paragraphs = text.find_elements_by_tag_name('p')
                for p in paragraphs:
                    article += p.text + " "

                temp_article = article

                temp_list = [None] * 3
                temp_list[0] = temp_link
                temp_list[1] = temp_title
                temp_list[2] = temp_article

                data[index] = temp_list
                index += 1

                if index % 10 == 0:
                    print(f"Just got data on article {index}. (Harvest time: {time.time() - end_time} seconds)")

            except Exception:

                print(f":( Failed to get {link}")

                continue

        self.data = data

    def save_data(self):

        desc = f"From The Blaze. First index is URL, second is title, third is content. Obtained on {datetime.date.today()}"

        pickle_out = open(f'./data/blaze_data_{self.harvest_range[0]}-{self.harvest_range[1]}.pkl', 'wb')
        pickle.dump((self.data, desc), pickle_out)
        pickle_out.close()

    def set_links(self):

        pickle_in = open('./data/blaze_links.pkl', 'rb')
        links, description = pickle.load(pickle_in)

        all_links = links
        to_visit = []

        first = self.harvest_range[0]
        last = self.harvest_range[1]

        for i in range(last - first):
            to_visit.append(all_links[i + first])

        self.links = to_visit

    def save_links(self):

        desc = f"Links from The Blaze to harvest later. Got {len(self.links)} links. Obtained on {datetime.date.today()}"

        pickle_out = open(f'./data/blaze_links_to_harvest.pkl', 'wb')
        pickle.dump((self.links, desc), pickle_out)
        pickle_out.close()

    def set_harvest_range(self, a, b):

        self.harvest_range = (a, b)

    def save_checked_links(self):

        desc = f"Links from The Blaze to harvest later. These are checked with bots.txt. Got {len(self.links)} links. Obtained on {datetime.date.today()}"

        pickle_out = open(f'./data/checked_blaze_links_to_harvest.pkl', 'wb')
        pickle.dump((self.links, desc), pickle_out)
        pickle_out.close()

    def run(self, ua):

        self.get_driver(ua)


        # start_t = time.time()
        # self.get_links()
        # print(f"Get_links took: {time.time() - start_t} seconds")

        # self.save_links()

        # maybe don't check bots.txt for each link?...there's going to be tons and tons (literally.) of links and I'm VERY confidant they're not controversial...how long would it take?
        # self.check_links()

        # self.save_checked_links()

        self.set_links()

        start_time = time.time()
        self.get_data()
        print(f"Got {len(self.links)} articles in {time.time() - start_time} seconds")

        self.save_data()

        self.driver.quit()


if __name__ == "__main__":

    indeces = [(1900, 2212)]

    for i in range(1):

        a = indeces[i][0]
        b = indeces[i][1]

        spider = slate_crawler()

        user_agent = "Amherst College SURF 2018, contact salfeld2018Amherst.edu with any questions."

        spider.set_harvest_range(a, b)

        spider.run(user_agent)

