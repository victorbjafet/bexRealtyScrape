#this was my original program that just scraped a zillow results page and printed info
#i used some random code from online as a base and built all my programs off that
#didnt even save data, just proof of concept and learning how to parse html
#switched off zillow due to rate limiting


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import time


# import undetected_chromedriver as uc

# options = webdriver.ChromeOptions() 
# options.add_argument("start-maximized")
# driver = uc.Chrome(options=options)
# driver.get('https://bet365.com')


l=list()
obj={} #dict
target_url = "https://www.zillow.com/cincinnati-oh/sold/"
driver=webdriver.Edge()
driver.get(target_url)


# html = driver.find_element(By.TAG_NAME, 'html')

# action = ActionChains(html)

# html.send_keys(Keys.END)
# html.send_keys(Keys.TAB)
# time.sleep(1)
# action.key_down(Keys.RETURN)
# action.key_up(Keys.RETURN)

# time.sleep(15)
x = ""
while x != "q":
    x = input()
    resp = driver.page_source #get page source

    soup=BeautifulSoup(resp,'html.parser') #init beautifulsoup parser object
    properties = soup.find_all("div",{"class":"StyledPropertyCardDataWrapper-c11n-8-84-3__sc-1omp4c3-0 bKpguY property-card-data"}) #find all elements that include housing data
    for x in range(0,len(properties)): #loop thru all of the found elements
    # for x in range(1):
            try:
                obj["pricing"]=properties[x].find("div",{"class":"StyledPropertyCardDataArea-c11n-8-84-3__sc-yipmu-0 fDSTNn"}).text
            except:
                obj["pricing"]=None
            try:
                temp = properties[x].find("div",{"class":"StyledPropertyCardDataArea-c11n-8-84-3__sc-yipmu-0 dbDWjx"}).text
                obj["beds"]=temp[0:temp.find("bds")-1]
                obj["bath"]=temp[temp.find("bds")+3:temp.find("ba")-1]
                obj["sqft"]=temp[temp.find("ba")+2:temp.find("sqft")-1]
                obj["status"]=temp[temp.rfind("-")+2:]
            except:
                obj["size"]=None
            try:
                obj["address"]=properties[x].find("a",{"class":"StyledPropertyCardDataArea-c11n-8-84-3__sc-yipmu-0 jnnxAW property-card-link"}).text
            except:
                obj["address"]=None
            l.append(obj)
            print(obj)
            obj={}

driver.close()

print(l)