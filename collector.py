import re
import DatabaseCredentials as dbc
import psycopg2 as db
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(chrome_options=options)
url = "https://scholar.google.com/citations?hl=en&user=%s&pagesize=100&view_op=list_works"
idSet = set()
checkedSet = set()


#Connect to PostgreDatabase
dbConnection = db.connect(database=dbc.DATABASE,user=dbc.USER,password=dbc.PASSWORD)
cursor = dbConnection.cursor()
#get targetList
cursor.execute("SELECT id FROM scientists_data")
for record in cursor:
    text = re.search('\(\'(.*)\',\)',str(record))
    idSet.add(text.group(1))

#get Checked List
cursor.execute("SELECT id FROM checked_scientists")
for record in cursor:
    text = re.search('\(\'(.*)\',\)',str(record))
    checkedSet.add(text.group(1))

#Perform collecting for each Scientist
for scientist in idSet:
    if checkedSet.__contains__(scientist):
        continue
    else:
        driver.get(url % scientist)

        sBarChart = driver.find_element_by_id("gsc_g")
        sBarChart.click()
        def find(driver):
            elements = driver.find_elements_by_id("gsc_md_hist_b")
            return elements
        element = WebDriverWait(driver,5).until(find)

        BS = BeautifulSoup(driver.page_source,"html.parser")
        mainBarChart = BS.find_all("div",id = "gsc_md_hist_b")
        RawHTML = BeautifulSoup(str(mainBarChart),"html.parser")
        years = RawHTML.find_all("span", class_ = "gsc_g_t")
        values = RawHTML.find_all("span", class_ = "gsc_g_al")

        #Extract Scientist Name
        scientistNameExt = BS.find("div",id = "gsc_prf_in")
        m = re.search('([A-z ]*)',scientistNameExt.text)
        if m:
            scientistName = m.group(1)

        #Extract h_index and h10_index
        h_indexes = BS.find_all("td", class_="gsc_rsb_std")
        h_index = h_indexes[2].text
        h10_index =  h_indexes[4].text


        scientistData = {}
        for i in range(0,years.__len__()-1,1):
            scientistData.__setitem__(int(years[i].text),int(values[i].text))

        sciList = list()

        sciList.append(str(scientistName))
        sciList.append(str(h_index))
        sciList.append(str(h10_index))
        for year in range(1977,2017,1):
            if scientistData.has_key(year):
                sciList.append(str(scientistData.get(year)))
            else:
                sciList.append(str(0))
        sciList.append(str(scientist))

        #prepare query
        query = "insert into scientists VALUES (%s)"
        sciList_text = re.search('\[(.*)\]',str(sciList))

        #Write in DB
        cursor.execute(query % sciList_text.group(1))
        dbConnection.commit()

        #Registrate Scientist
        query = "INSERT INTO checked_scientists VALUES (%s)"
        data = list()
        data.append(str(scientist))
        data_text = re.search('\[(.*)\]',str(data))
        cursor.execute(query % data_text.group(1))
        dbConnection.commit()

        # with open("outfile.txt","a") as outfile:
        #     outfile.write(scientistName + ',')
        #     for year in range(1977,2017,1):
        #         if scientistData.has_key(year):
        #             if year != 2016:
        #                 outfile.write(str(scientistData.get(year)) + ',')
        #             else:
        #                 outfile.write(str(scientistData.get(year)))
        #         else:
        #             if year != 2016:
        #                 outfile.write('0,')
        #             else:
        #                 outfile.write('0')
        #
        #     outfile.write('\n')
        # driver.close()

driver.close()

