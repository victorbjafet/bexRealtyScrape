import pandas as pd

dataframe = pd.read_json('data/bexrealty_scrape_data_columbus_ohio_raw.json', orient ='split') #reads in raw scraped data from json

og = len(dataframe)
dataframe = dataframe.dropna(axis=0,how="any") #drop all rows with any null values
new = og - len(dataframe) #calculate how many rows were dropped
print(str(new) + " rows with null values dropped")

print(str(len(dataframe)) + " complete rows of data")

#convert all float types into int types because idk why they all ended up being float types
dataframe['Bedrooms'] = dataframe['Bedrooms'].astype(int)
dataframe['Bathrooms'] = dataframe['Bathrooms'].astype(int)
dataframe['Year'] = dataframe['Year'].astype(int)
dataframe['Area'] = dataframe['Area'].astype(int)

dataframe.to_json('data/bexrealty_scrape_data_columbus_ohio_clean.json', orient = 'split', index = 'true') #saves the cleaned dataframe to json