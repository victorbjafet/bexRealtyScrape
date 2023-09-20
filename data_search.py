import pandas as pd
import os

pd.set_option('display.max_columns', None) #unrestrict amount of columns printable
pd.set_option('display.max_rows', None)  #unrestrict amount of rows printable
pd.set_option('display.max_colwidth', None)  #unrestrict printable width of columns

dataframe = pd.read_json('data/bexrealty_scrape_data_columbus_ohio_clean.json', orient ='split') #reads in data from json

#a little page search thing to explore the data
x = 0
resultsperpage = 25
while x >= 0:
    os.system('cls')
    print(dataframe[resultsperpage * x:resultsperpage * (x + 1)])
    x = int(input("page number: "))
