from logging import root
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import os
import time
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from msedge.selenium_tools import EdgeOptions, Edge

browser_type = 'chrome'
while browser_type == '':
    browser_type = input("Please enter browser name (chrome/firefox/edge): ")
    if browser_type != 'chrome' and browser_type != 'firefox' and browser_type != 'edge':
        browser_type = ''

if browser_type=='edge':
    options = EdgeOptions()
    # options.use_chromium = True
    options.add_argument('ignore-certificate-errors')
    driver = Edge(executable_path=EdgeChromiumDriverManager().install(), options=options)

if browser_type=='firefox':
    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())

if browser_type=='chrome':
    #Setting up options for the driver
    option = webdriver.ChromeOptions()
    option.add_argument("--disable-infobars")
    option.add_argument("start-maximized")
    option.add_argument("--disable-extensions")
    option.add_experimental_option('excludeSwitches', ['enable-logging'])
    option.add_argument('ignore-certificate-errors')
    # option.add_argument('headless')

    #Creating the driver
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=option)

#Loading the webpage
driver.get('https://blackbox.eastdelta.edu.bd/einstein-freshair/index.jsp')
root_window = driver.window_handles[0]
print('Webpage title: '+driver.title)

#Getting the login fields
username = driver.find_element_by_name("username")
password = driver.find_element_by_name("password")
loginButton = driver.find_element_by_id("loginBtn")
driver.find_element_by_xpath("//select[@name='role']/option[text()='Student']").click()

name= 'ayon3'
pword= 'asd123123'

username.send_keys(name)
password.send_keys(pword)
loginButton.click()

#---- Login Successful
# instr_surv_table = driver.find_element_by_id('instructor_survey')
# print(instr_surv_table.get_attribute('innerHTML'))

try:
    framesets = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.TAG_NAME, "frameset")))
    # print(framesets[1].get_attribute("innerHTML"))
    driver.switch_to.frame("mainframe")
    # print(driver.page_source)
    
    # Navigating to the 'instructor_survey' section
    instr_surv_table_id = "//table[@id='instructor_survey']"
    instr_surv_table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, instr_surv_table_id)))
    print("'instructor_survey' table found!")
    source_code = instr_surv_table.get_attribute("innerHTML")
    # print(source_code)

    coursesHref = driver.find_elements_by_xpath("//*[@id='instructor_survey']/tbody/tr/td/a")

    courses = []
    courseLinks = [] 
    for courseHref in coursesHref:
        courseTitle = courseHref.get_attribute("innerHTML")
        courses.append(courseTitle)
        courseLink = courseHref.get_attribute("href")
        courseLinks.append(courseLink)

    for courseTitle, courseLink in zip(courses, courseLinks):
        # driver.execute_script("arguments[0].target='_self';", courseHref)
        # courseLink.click()

        driver.execute_script("window.open()")
        time.sleep(1)
        # Switch to the newly opened tab
        driver.switch_to.window(driver.window_handles[1])
        # Navigate to new URL in new tab
        driver.get(courseLink)
        print('Webpage title: '+driver.title)

        # print((driver.page_source))
        spans = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "span")))
        instructor = spans[1].text[19:len(spans[1].text)-1]

        print("Course: "+courseTitle+" - Instructor: "+instructor)
        print("Points criteria : \n 5) Strongly Agree \n 4) Agree \n 3) Neutral \n 2) Disagree \n 1) Strongly Disagree")

        def representsInt(s):
            try: 
                int(s)
                return True
            except ValueError:
                return False

        reviewPoint = 0
        while (reviewPoint==0):
            reviewPoint = input("What points do you want to give (1-5): ")
            if representsInt(reviewPoint):
                reviewPoint = int(reviewPoint)
                if not (1<=reviewPoint<=5):
                    reviewPoint = 0
            else:
                reviewPoint = 0
        
        # print("Your selected point: "+str(reviewPoint))

        comment = ''
        while comment=='':
            comment = input("Comment and suggestions: ").strip()

        # -------- Page 1
        radios = []
        nextButton = ''
        inputs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))
        for input in inputs:
            if input.get_attribute("type") == 'radio':
                # print(input.get_attribute("onclick"))
                radios.append(input)
            if input.get_attribute("name") == 'Next':
                nextButton = input
                # print("next button found")
        # print(len(radios))

        for radio in radios:
            onclick = radio.get_attribute("onclick")
            optionNo = int(onclick[len(onclick)-3:len(onclick)-2])
            if optionNo == reviewPoint:
                radio.click()

        nextButton.click()


        # -------- Page 2
        radios = []
        finishButton = ''
        inputs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))
        for input in inputs:
            if input.get_attribute("type") == 'radio':
                # print(input.get_attribute("onclick"))
                radios.append(input)
            if input.get_attribute("name") == 'Finish':
                finishButton = input
                print("finish button found")

        for radio in radios:
            onclick = radio.get_attribute("onclick")
            optionNo = int(onclick[len(onclick)-3:len(onclick)-2])
            if optionNo == reviewPoint:
                radio.click()

        commentBox = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
        commentBox.send_keys(comment)

        # finishButton.click()

        time.sleep(2)
        driver.switch_to.window(root_window)
        # break



except TimeoutException:
    print("No 'instructor_survey' table found")

