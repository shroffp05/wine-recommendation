import pandas as pd 
import numpy as np 
import pycountry


def update_df(data, img_df, recc):

	data.Name = data.Name.apply(lambda x: x.lower())
	data.rename(columns={'Unnamed: 0': 'ID'}, inplace=True)

	recc.rename(columns={'Unnamed: 0': 'Name'}, inplace=True)
	recc['ID'] = np.arange(len(recc))

	img_df.rename(columns={'Unnamed: 0': 'ID'}, inplace=True)

	return data, img_df, recc 


def extract_country(app):

	for country in pycountry.countries:
		if country.name in app:
			return country.name  
		else:
			if "USA" in app:
				return "USA"
	

def extract_abv(abv):
    abv = abv[:-1]
    abv = abv.replace(",", ".")
    return float(abv)

def extract_price(price):
    return float(price[1:])


def feature_eng_data(data):

	data['Appellation'] = data['Appellation'].fillna("USA")
	data.loc[data['Price']=='$','Price'] = "$21.00"


	data['Blend/Variety'] = np.where(data.Blend.isna(), data.Variety, data.Blend)
	data.Vintage = data.Vintage.fillna("NV")

	data['abv'] = data['ABV'].apply(lambda x: extract_abv(x)) 
	data['price'] = data['Price'].apply(lambda x: extract_price(x))

	data['Country'] = data.Appellation.apply(lambda x: extract_country(x))

	fill_vals = {'Pine Mountain-Cloverdale': 'USA', 'Howell Mountain': 'USA', "Val D'aosta": "Italy", "Seneca Lake": "USA", 
            "Pennsylvania": "USA", "sonomaSonoma County": "USA", "England": "UK", "Knights Valley": "USA", 
            "Stag's Leap District": "USA", "Amyndeon": "Greece", "Coonawarra": "Australia", "Chinon": "France", 
            "Yarra Valley": "Australia", "Franschhoek Valley": "South Africa", "Pfalz": "Germany", "Attica": "Greece",
            "Hermitage": "France", "Umpqua Valley": "USA", "Waipara Valley": "New Zealand"}

	data.Country = data.Country.fillna(data.Appellation.map(fill_vals))
	data.Country = data.Country.fillna("France")

	fill_vals = {"Jadix Picpoul de Pinet 2019": "Picpoul Blanc",
             "Tablas Creek Vineyard Esprit Blanc 2019": "Roussane, Grenache Blanc, Picpoul Blanc, Picardan",
             "Tablas Creek Vineyard Esprit de Tablas 2019": "Mourvedre, Grenache, Syrah, Counoise",
             "Koncho & Co Kisi Qvevri 2019": "White Dry", 
             "Teliani Valley Amber Blend 2019": "Amber Blend"}

	data['Blend/Variety'] = data['Blend/Variety'].fillna(data['Name'].map(fill_vals))

	data['Perfect For'] = data['Perfect For'].fillna('NA')
	data['Drink If You Like'] = data['Drink If You Like'].fillna('NA')

	#cols_to_drop = ["Blend", "ABV", "Price", "Variety", "Reviewed By", "Reviewed", "Review Updated"]

	#data.drop(columns=cols_to_drop, inplace=True)

	return data 
