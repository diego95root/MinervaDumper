from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time, os, requests

class Downloader:
    def __init__(self, subject, location):
        self.subject = subject
        self.location = location
        self.links = []

    def create_dir(self):
        path = '{}/{}_files'.format(os.path.dirname(os.path.realpath(__file__)), self.subject)
        os.system("mkdir '{}' && cd '{}'".format(path, path))
        self.path = path

    def webdriver_create(self):
        chromeOptions = webdriver.ChromeOptions()
        prefs = {"plugins.always_open_pdf_externally": True, "download.default_directory" : '{}_files'.format(self.subject)}
        chromeOptions.add_experimental_option("prefs",prefs)
        chromeOptions.add_argument("--headless")
        driver = webdriver.Chrome(executable_path="chromedriver", chrome_options=chromeOptions)
        self.driver = driver

    def login(self, user, pwd):
        self.driver.get("http://minerva.leeds.ac.uk")
        elem = self.driver.find_element_by_id("userNameInput")
        elem.send_keys(user)
        elem = self.driver.find_element_by_id("passwordInput")
        elem.send_keys(pwd)
        elem.send_keys(Keys.RETURN)


    def get_module(self):
        self.driver.get("https://minerva.leeds.ac.uk/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_209_1")

        elem = self.driver.find_elements_by_xpath('//*[@id="vleModules"]/tbody/tr[*]/td[3]/label/a')

        for i in elem:
            if i.get_attribute('text') == self.subject:
                break

        self.driver.get(i.get_attribute("href"))

    def get_location(self):
        l = self.driver.find_elements_by_xpath('//*[@id="courseMenuPalette_contents"]')[0]

        for x in l.find_elements_by_tag_name("li"):
            anchor = x.find_elements_by_tag_name("a")
            if len(anchor) == 1:
                if anchor[0].get_attribute("text") == self.location:
                    break

        self.driver.get(anchor[0].get_attribute("href"))

    def get_links(self):
        elems = self.driver.find_elements_by_xpath("//a[@href]")
        for elem in elems:
            if "bbcswebdav" in elem.get_attribute("href"):
                self.links.append([(elem.get_attribute("href")).encode('ascii','ignore'), (elem.get_attribute("text")).encode('ascii','ignore')])

# It'd be faster to not run it headless and do driver.get but this way I hide the browser
    def download_links(self):
        cookies = self.driver.get_cookies()
        s = requests.Session()
        for cookie in cookies:
            s.cookies.set(cookie['name'], cookie['value'])

        for i in self.links:
            print "[*] --> {}".format(i[1])
            with open('{}/{}'.format(self.path, i[1]), 'wb') as f:
                f.write(s.get(i[0]).content)

    def download(self, username, pwd):
        self.create_dir()
        print "[*] Creating the directory under: {}...".format(self.path)
        self.webdriver_create()
        print "[*] Logging in to Minerva..."
        self.login(username, pwd)
        print "[*] Selecting the module..."
        self.get_module()
        print "[*] Going to the module page..."
        self.get_location()
        print "[*] Getting files URL..."
        self.get_links()
        print "[*] Starting download:"
        self.download_links()
        print "[*] Everything downloaded, quitting..."
        self.quit()

    def quit(self):
        self.driver.quit()

if __name__=="__main__":
    user = ""
    pwd = ""

    architecture = Downloader("Computer Architecture", "Lectures")
    architecture.download(user, pwd)

    print "\n"

    professional = Downloader("Professional Computing", "Learning Resources")
    professional.download(user, pwd)
