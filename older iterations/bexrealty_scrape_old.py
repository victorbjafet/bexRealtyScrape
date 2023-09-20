#was intended to be the final version of my scraper
#the city i used with this scraper (cincinnati) had too much missing information for most houses
#i chose to make a slightly better version of the scraper that was entirely auto with no page number entering and a couple fixes (error crash prevention)


from bs4 import BeautifulSoup #html parser

from selenium import webdriver #html requesting, loading js and getting page source
from selenium.webdriver.chrome.options import Options

import pandas as pd #data storing

pd.set_option('display.max_columns', None) #unrestrict amount of columns printable
pd.set_option('display.max_rows', None)  #unrestrict amount of rows printable
pd.set_option('display.max_colwidth', None)  #unrestrict printable width of columns


options = Options()
# options.add_argument("--headless=new") #uncomment if you dont want a browser window opening (may possibly be faster but im not sure)
driver = webdriver.Chrome(options=options) #web driver (basically what browser is going to be running the requests)

data = list() #array that will contain other arrays (which are the rows of fetched data) inside it. at the end of the program this array become a pandas dataframe with each array inside it representing a row

def check_nan(string,pool=False,area=False): #this function is for when the raw text data is being parsed, each part goes through this check in case the data happens to not exist, and there are specific cases which are accounted for using boolean parameters
    if string == "—": #if the text that is passed into the function is a dash, it means the data does not exist so return None
        return None
    elif pool == True: #if the data being checked for nan is pool data and it is not None, return just the string
        return string 
    elif area == True: #if the data being checked for nan is the area of the house and it is not None, return a parsed, integer version of the value (area value specifically has to be parsed in a certain way to get the integer)
        return int(string.replace(",", "")[:-6]) #removes the "Sq Ft" at the end and also the comma in the number, allowing it to become an integer
    else:
        try: #try to convert the string to integer and return
            return int(string)
        except: #if it doesnt work, it means that there is a half bathroom. for simplicity, we count all bathrooms as full bathrooms
            return int(string[:string.find(" ")]) + int(string[string.rfind(" ") + 1:]) #just get the integers for both the amount of half bathrooms and full bathrooms and add them together
    

page_num = 1 #page num needs to be initialized before starting the while loop, so make it one. this means the scrape will always occur once on the first page of results
while page_num != 0: #zero will stop the loop and save the data
    #part 1: scrape the search results page to get all links to house pages
    print("Scraping page " + str(page_num) + " of search results")
    driver.get("https://www.bexrealty.com/Ohio/Cincinnati/?propertype=single-family-home,condominium,townhouse&page_number=" + str(page_num)) #gets the search results page that the user inputted (or the first if the loop is running for the first time)
    page_source = driver.page_source #get page source
    results_parse = BeautifulSoup(page_source,'html.parser') #init beautifulsoup parser object
    listing_cards = results_parse.find_all("div",{"class":"listing-card"}) #find all elements that have a clickable link to a house's page
    link_results = list() #make a list where all these links will be stored
    for card in range(0,len(listing_cards)): #loop thru all of the found elements containing links
    # for card in range(1): #for debug when a certain link needs to be tested
        link_results.append("https://www.bexrealty.com" + listing_cards[card].find("a").get('href')) #get the "a" element withing each div and its hrefs (link) as well as append the beginning of the website link since it only returns the end
        print(link_results[-1]) #print the last found link (basically the link above)
    print(str(len(link_results)) + " search results found on page " + str(page_num)) #print amount of links found

    #part 2: scrape each individual house link for house details
    for link in link_results: #does this entire scrape process once for every single link found on the search results page
        data_list = list() #creates a list that will be the row of data for this specific house
        driver.get(link) #gets the link of the specific house's page
        # driver.get("https://www.bexrealty.com/Ohio/Cincinnati/1238-Elsinore-Ave/single-family-home/") #for debug when a certain link needs to be tested
        page_source = driver.page_source #get page source
        house_parse = BeautifulSoup(page_source,'html.parser') #init beautifulsoup parser object

        address = house_parse.find("h1",{"class":"page-header"}).text #get address of house
        for i in range(2):
            address = address[:address.find("\n")] + address[address.find("\n") + 12:] #gets rid of random whitespace in address text
        data_list.append(address) #add address to row of data

        price = house_parse.find("p",{"class":"listing-price"}).text.replace(",", "")
        data_list.append(int(price[price.rfind("$") + 1:-1])) #get price of house and adds it to row of data (also only starts accounting for price at last instance of a dollar sign due to the possibility of a discount being displayed)

        features = house_parse.find_all("div",{"class":"features-grid-outside"}) #find all elements that have info about the house
        data_list.append(check_nan(features[0].text[10:11])) #add bedrooms to row
        data_list.append(check_nan(features[1].text[11:12])) #bathrooms to row
        data_list.append(check_nan(features[2].text[8:9])) #garages to row
        data_list.append(check_nan(features[3].text[17:-9],pool=True)) #pool to row
        data_list.append(check_nan(features[4].text[12:])) #year built to row
        data_list.append(check_nan(features[5].text[13:],area=True)) #area square feet to row

        print(data_list) #prints the completed row of data, showing all attributes that were found for the house
        if data_list[1] > 10000:
            data.append(data_list) #adds the row to the list that will eventually become the pandas dataframe
        else:
            print("house not added due to abnormal price")

    print(len(data)) # show the user how many rows of data have been collected

    #stuff that makes sure that the users input wont be a non int and cause problems in the while condition
    is_int = False
    while is_int == False:
        page_num = input("Input the results page number you would like to scrape (or 0 to stop): ")
        try:
            page_num = int(page_num)
            is_int = True
        except:
            print("not an integer. try again")

#closes the browser session
driver.quit()

dataframe = pd.DataFrame(data, columns=['Address', 'Price', 'Bedrooms', 'Bathrooms', 'Garages', 'Pool', 'Year', 'Area']) #turns the entire "data" list into a pandas dataframe, adding the columns too
# print(dataframe) #this could explode my pc depending on the amount of data collected so ill stick to reading the json file from now on
dataframe.to_json('bex_realty_housing_scraped_data.json', orient = 'split', index = 'true') #saves the dataframe to json (already tested to make sure it loads back the same exact way)

# readtest = pd.read_json('bex_realty_housing_scraped_data.json', orient ='split', compression = 'infer') #to read the data in if needed in the future