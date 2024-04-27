from time import sleep

from bs4 import BeautifulSoup #html parser

from selenium import webdriver #html requesting, loading js and getting page source
from selenium.webdriver.chrome.options import Options

import pandas as pd #data storing

pd.set_option('display.max_columns', None) #unrestrict amount of columns printable
pd.set_option('display.max_rows', None)  #unrestrict amount of rows printable
pd.set_option('display.max_colwidth', None)  #unrestrict printable width of columns


options = Options()
# options.add_argument("--headless=new") #uncomment if you dont want a browser window opening (may possibly be faster but im not sure)
options.add_experimental_option('excludeSwitches', ['enable-logging']) #get rid of the stupid windows USB error messages that keep appearing
driver = webdriver.Chrome(options=options) #web driver (basically what browser is going to be running the requests)

data = list() #array that will contain other arrays (which are the rows of fetched data) inside it. at the end of the program this array become a pandas dataframe with each array inside it representing a row

def check_nan(string,pool=False,area=False): #this function is for when the raw text data is being parsed, each part goes through this check in case the data happens to not exist, and there are specific cases which are accounted for using boolean parameters
    if string == "—": #if the text that is passed into the function is a dash, it means the data does not exist so return None
        return None
    elif pool == True: #if the data being checked for nan is pool data and it is not None, return just the string
        if string != "No":
            return True
        else:
            return False
    elif area == True: #if the data being checked for nan is the area of the house and it is not None, return a parsed, integer version of the value (area value specifically has to be parsed in a certain way to get the integer)
    #     return int(string.replace(",", "")[:-6]) #removes the "Sq Ft" at the end and also the comma in the number, allowing it to become an integer
        try:
            return int(string.replace(",", ""))
        except:
            return None
    else:
        try: #try to convert the string to integer and return
            return int(string)
        except: #if it doesnt work, it means that there is a half bathroom. for simplicity, we count all bathrooms as full bathrooms
            return int(string[:string.find(" ")]) + int(string[string.rfind(" ") + 1:]) #just get the integers for both the amount of half bathrooms and full bathrooms and add them together

#make sure the user doesnt enter non int value
is_int = False
while is_int == False:
    page_num = input("Input the number of pages you would like to scrape: ")
    try:
        page_num = int(page_num)
        is_int = True
    except:
        print("Not an integer, try again")

errors = 0 #just tracking how many errors occur cuz y not (3 happened in a 1.8k 40 page scrape idk what caused them)
for page in range(page_num):
    #part 1: scrape the search results page to get all links to house pages
    print("Scraping page " + str(page + 1) + " of search results")
    driver.get("https://www.bexrealty.com/Ohio/Columbus/?propertype=condominium,single-family-home,home&page_number=" + str(page + 1)) #gets the search results page that the user inputted (or the first if the loop is running for the first time)
    page_source = driver.page_source #get page source
    results_parse = BeautifulSoup(page_source,'html.parser') #init beautifulsoup parser object
    listing_cards = results_parse.find_all("div",{"class":"listing-card"}) #find all elements that have a clickable link to a house's page
    link_results = list() #make a list where all these links will be stored
    for card in range(0,len(listing_cards)): #loop thru all of the found elements containing links
    # for card in range(1): #for debug when a certain link needs to be tested
        try:
            link_results.append("https://www.bexrealty.com" + listing_cards[card].find("a").get('href')) #get the "a" element withing each div and its hrefs (link) as well as append the beginning of the website link since it only returns the end
            print(link_results[-1]) #print the last found link (basically the link above)
        except:
            print("link broke")
    print(str(len(link_results)) + " search results found on page " + str(page + 1)) #print amount of links found


    #part 2: scrape each individual house link for house details
    for link in link_results: #does this entire scrape process once for every single link found on the search results page
        data_list = list() #creates a list that will be the row of data for this specific house
        driver.get(link) #gets the link of the specific house's page
        # driver.get("https://www.bexrealty.com/Ohio/Reynoldsburg/3005-Hollybank-Rd/single-family-home/") #for debug when a certain link needs to be tested
        sleep(1)
        page_source = driver.page_source #get page source
        house_parse = BeautifulSoup(page_source,'html.parser') #init beautifulsoup parser object

        try:
            address = house_parse.find("h1",{"class":"page-header"}).text #get address of house
            data_list.append(address[:-20].strip()) #add address to row of data

            price = house_parse.find("p",{"class":"listing-price"}).text.replace(",", "") #get price element and get rid of commas for efficiency
            try:
                price = int(float(price[price.rfind("$") + 1:])) #convert price to float first in case it is a float (rounds down so 299999.99 becomes 299999), also only starts accounting for price at last instance of a dollar sign due to the possibility of a discount being displayed
            except:
                price = int(float(price[price.rfind("$") + 1:price.find(" ")])) #if there was an error above, likely means that the house has "bank owned" at the end so just get the first word of the string which is the price
            data_list.append(price) #get adds price to row of data ()

            features = house_parse.find("div",{"class":"features-grid"}) #find all elements that have info about the house
            
            beds = features.find("div",{"class":"bed"}).text
            data_list.append(check_nan(beds[:beds.find("Bedrooms") - 1])) #add bedrooms to row

            baths = features.find("div",{"class":"bath"}).text
            data_list.append(check_nan(baths[:baths.find("Bathrooms") - 1])) #bathrooms to row

            garages = features.find("div",{"class":"garage"}).text
            data_list.append(check_nan(garages[:garages.find(" ")])) #garages to row

            pool = house_parse.find("ul",{"aria-label":"Pool"}).text
            data_list.append(check_nan(pool,pool=True)) #pool to row

            year = features.find("div",{"class":"year"}).text
            data_list.append(check_nan(year[year.find("in") + 2:])) #year built to row

            sqft = features.find("div",{"class":"sqft"}).text
            data_list.append(check_nan(sqft[:sqft.find(" ")],area=True)) #area square feet to row

            print(data_list) #prints the completed row of data, showing all attributes that were found for the house
            
            if data_list[1] > 25000:
                data.append(data_list) #adds the row to the list that will eventually become the pandas dataframe
            else:
                print("House not added due to abnormal price")
        except:
            print(link + " resulted in an error when parsing and was skipped") #if some error occurs during the html parsing or the value parsing then just skip it and enumerate the error counter
            errors += 1
            input("enter when next")
        

    print(str(len(data)) + " rows of data currently collected") # show the user how many rows of data have been collected after each scraped page

        

#closes the browser session
driver.quit()

print("Scraping complete, " + str(len(data)) + " rows of data collected")
print(str(errors) + " errors occurred during the parsing of the collected data")

dataframe = pd.DataFrame(data, columns=['Address', 'Price', 'Bedrooms', 'Bathrooms', 'Garages', 'Pool', 'Year', 'Area']) #turns the entire "data" list into a pandas dataframe, adding the columns too
print("Data converted into a pandas dataframe")
# print(dataframe) #this could explode my pc depending on the amount of data collected so ill stick to reading the json file from now on

dataframe.to_json('bexrealty_scrape_data_city_state_raw.json', orient = 'split', index = 'true') #saves the dataframe to json (already tested to make sure it loads back the same exact way)
print("Data saved to json file \"bexrealty_scrape_data_city_state_raw.json\"")

# readtest = pd.read_json('bex_realty_housing_scraped_data.json', orient ='split', compression = 'infer') #to read the data in if needed in the future