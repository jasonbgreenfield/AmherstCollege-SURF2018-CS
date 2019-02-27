import pickle
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import NoSuchElementException
from urllib import robotparser

class slate_crawler(object):

    def __init__(self):

        self.driver = webdriver.Chrome()

        self.links = []

        self.data = []

    def get_driver(self, ua):

        opts = Options()
        opts.add_argument(f"user-agent={ua}")
        to_return = webdriver.Chrome(chrome_options=opts)
        to_return.get("https://www.google.com/")

    def get_links(self):

        max_pages = 1 # number of pages (of 20 articles each of the two pages) that we'll scroll through) (the total num_articles = 40*max_pages))
        gathered_links = []

        num_links = 0
        for i in range(2):
            if i == 0:
                self.driver.get("https://slate.com/news-and-politics?via=homepage_nav")
            if i == 1:
                self.driver.get("https://slate.com/business?via=section_nav")
            for j in range(max_pages):
                for k in range(1, 21):
                    link = self.driver.find_element_by_xpath(f"""//*[@id="main"]/div/section/div[3]/div[1]/div/a[{k}]""").get_attribute('href')
                    gathered_links.append(link)
                    num_links += 1
                    if num_links % 100 == 0:
                        print(f"Just grabbed the {num_links}th link!")
                if j == 0:
                    self.driver.find_element_by_xpath("""//*[@id="main"]/div/section/div[3]/div[1]/div/nav/ul/li/a""").click()
                else:
                    self.driver.find_element_by_xpath("""//*[@id="main"]/div/section/div[3]/div[1]/div/nav/ul/li[2]/a""").click()

        gathered_links = set(gathered_links)

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
            rp.set_url(self.get_robo_link(l))
            rp.read()
            if rp.can_fetch("*", l):
                checked_links.append(l)
        self.links = checked_links


    def get_data(self):

        to_visit = self.links
        data = [[]]*len(to_visit)
        print(len(data))

        index = 0
        for link in to_visit:
            self.driver.get(link)

            temp_link = link

            temp_title = self.driver.find_element_by_class_name('article__hed').text

            article = ""
            paragraphs = self.driver.find_elements_by_class_name('slate-paragraph')
            for p in paragraphs:
                article += p.text + " "
            temp_article = article

            temp_list = [None]*3
            temp_list[0] = temp_link
            temp_list[1] = temp_title
            temp_list[2] = temp_article

            data[index] = temp_list
            index += 1
            if index%100 == 0:
                print(f"Just got data on the {index}th article!")

        self.data = data

    def save_data(self):

        desc = f"From Slate. First index is URL, second is title, third is content. Obtained on {datetime.date.today()}"

        pickle_out = open(f'./data/slate_data.pkl', 'wb')
        pickle.dump((self.data, desc), pickle_out)
        pickle_out.close()

    def run(self, ua):

        self.get_driver(ua)

        self.get_links()

        self.check_links()

        self.get_data()

        self.save_data()

        self.driver.quit()


if __name__ == "__main__":

    spider = slate_crawler()

    user_agent = "Amherst College SURF 2018, contact salfeld2018Amherst.edu with any questions."

    spider.run(user_agent)

    # Note: took 427 seconds to grab 1000 links (not process them, just grab)
