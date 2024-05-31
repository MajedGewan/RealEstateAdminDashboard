import pandas as pd
data = None
visits = None
def get_visit_data():
    global visits
    if visits is None:
        data = pd.read_csv('visits.csv')
    return data
def get_data():
    global data
    if data is None:
        data = pd.read_csv('data.csv')
    return data
def filter_data(data, price, size, houses, neighborhoods, sources, bedrooms, quality):
    returned_data = data
    if price:
        price_from = price[0]
        price_to = price[1]
        returned_data = returned_data[(returned_data['Price']>=price_from) & (returned_data['Price']<=price_to)]
    if size:
        size_from = size[0]
        size_to = size[1]
        returned_data = returned_data[(returned_data['Size(sqft)']>=size_from) & (returned_data['Size(sqft)']<=size_to)]
    if bedrooms:
        bedroom_from = bedrooms[0]
        bedroom_to = bedrooms[1]
        returned_data = returned_data[(returned_data['Bedrooms']>=bedroom_from) & (returned_data['Bedrooms']<=bedroom_to)]
    if houses:
        returned_data = returned_data[returned_data['House'].isin(houses)]
    if neighborhoods:
        returned_data = returned_data[returned_data['Neighborhood'].isin(neighborhoods)]
    if sources:
        returned_data = returned_data[returned_data['Source'].isin(sources)]
    if quality:
        returned_data = returned_data[returned_data['Quality'].isin(quality)]
    else:
        returned_data = returned_data[returned_data['Quality'] == 'False']
    return returned_data

def get_price_range():
    data = get_data()
    price_from = data['Price'].min()
    price_to = data['Price'].max()
    return price_from, price_to

def get_size_range():
    data = get_data()
    size_from = data['Size(sqft)'].min()
    size_to = data['Size(sqft)'].max()
    return size_from, size_to

def get_bedroom_range():
    data = get_data()
    bedroom_from = data['Bedrooms'].min()
    bedroom_to = data['Bedrooms'].max()
    return bedroom_from, bedroom_to

def get_neighborhoods():
    data = get_data()
    neighborhoods = data['Neighborhood'].to_list()
    return neighborhoods
def get_houses():
    data = get_data()
    houses = data['House'].to_list()
    return houses
def get_sources():
    data = get_data()
    sources = data['Source'].unique()
    return sources
def get_total_sales(start_date, end_date):
    visits = get_visit_data()
    successfull = visits[(visits['deal'] == True) & (visits['date'] >= start_date) & (visits['date'] <= end_date)]
    total_sales = successfull['price'].sum()
    return total_sales
def get_visits_deals(start_date, end_date):
    visits = get_visit_data()
    successfull = visits[(visits['date'] >= start_date) & (visits['date'] <= end_date)]
    visits_count = successfull.shape[0]
    deals = successfull[successfull['deal'] == True].shape[0]
    return visits_count, deals