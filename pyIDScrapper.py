from bs4 import BeautifulSoup
from selenium import webdriver
import re
import psycopg2 as db
import DatabaseCredentials as dbc

chrome = webdriver.Chrome()
labels = ["particle_physics","nanotechnology","computer_science", "statistics","Psychology","politics","finance","chemistry","physics","mathematics","clustering","biology","medicine","networks"]
scientistsSet = set()

dbConnection = db.connect(database=dbc.DATABASE,user=dbc.USER,password=dbc.PASSWORD)
cursor = dbConnection.cursor()
cursor.execute("select id from scientists_data;")
for record in cursor:
    text = re.search('\(\'(.*)\',\)',str(record))
    scientistsSet.add(text.group(1))


for label in labels:

    url = "https://scholar.google.com/citations?view_op=search_authors&hl=en&mauthors=label:" + label
    chrome.get(url)

    for page in range(0,10,1):
        def find(driver):
            elements = driver.find_element_by_css_selector('button[aria-label*="Next"]')
            return elements

        nextButton = chrome.find_element_by_css_selector('button[aria-label*="Next"]')
        rawHTML = BeautifulSoup(chrome.page_source, "html.parser")
        links = chrome.find_elements_by_css_selector('.gsc_1usr_name > a[href^="/citations?user"]')

        for i in links:
            scientistId = re.search('.*user=(.*)&.*', i.get_attribute("href"))
            if scientistId:
                scientistName = scientistId.group(1)
            if scientistsSet.__contains__(scientistName):
                continue
            else:
                scientistsSet.add(scientistName)
                SQL = "insert into scientists_data values (%s,%s)"
                data = (scientistName,label)
                cursor.execute(SQL,data)
                dbConnection.commit()

        nextButton.click()

chrome.close()
