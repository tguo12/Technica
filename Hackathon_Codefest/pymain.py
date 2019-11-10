import pandas as pd
import numpy as np
import re
import json
import pgeocode
from geopy.distance import geodesic



def locate_city_data(city_name):
    df_business = df_business[df_business.city == city_name]
    unique_df_business_ids = df_business.business_id.unique()
    df_tip = df_tip[df_tip['business_id'].isin(unique_df_business_ids)]
    df_review = df_review[df_review['business_id'].isin(unique_df_business_ids)]


def search_for_restaurant(categories):
    list = []
    for word in categories:
        for i in range(0, len(df_business)):
            if word in str(df_business.categories[i]).lower():
                if df_business['business_id'][i] not in list:
                    list.append(df_business['business_id'][i])
    return df_business[df_business['business_id'].isin(list)]


def top_5_restaurant(business_data):
    # filter out business with very few review count
    business_data = business_data[business_data.distance < 10]
    business_data = business_data[business_data.review_count > 20]
    business_data = business_data.sort_values('stars', ascending=False).head(5)
    business_data = business_data.sort_values('review_count', ascending=False)
    business_data.index = np.arange(1, len(business_data) + 1)
    return business_data


def distance_calculator(zipcode):
    distance_list = []
    nomi = pgeocode.Nominatim('us')
    zip_loc = (nomi.query_postal_code(zipcode).latitude, nomi.query_postal_code(zipcode).longitude)
    for i in range(0, len(df_business)):
        business_loc = (df_business['latitude'][i], df_business['longitude'][i])
        distance_list.append(geodesic(zip_loc, business_loc).miles)
    df_business['distance'] = distance_list


def name_of_restaurant_list(dataframe):
    return dataframe.name


# run this after business category is selected
def filtered_business_review(data):
    unique_df_business_ids = data.business_id.unique()
    return df_review[df_review['business_id'].isin(unique_df_business_ids)]


# run this after business category is selected
def filtered_business_tip(data):
    unique_df_business_ids = data.business_id.unique()
    return df_tip[df_tip['business_id'].isin(unique_df_business_ids)]


# personal preference, single word
def restaurant_relative(keywords, data):
    unique_df_business_ids = data.business_id.unique()
    data_reviews = filtered_business_review(data)
    data_reviews.index = np.arange(0, len(data_reviews))
    data_tips = filtered_business_tip(data)
    data_tips.index = np.arange(0, len(data_tips))

    for word in keywords:
        for i in range(0, len(data_reviews)):
            if word in str(data_reviews.text[i]).lower():
                id = data_reviews['business_id'][i]
                df_business.loc[df_business['business_id'] == id, 'score'] += 1
    for word in keywords:
        for i in range(0, len(data_tips)):
            if word in str(data_tips.text[i]).lower():
                id = data_tips['business_id'][i]
                df_business.loc[df_business['business_id'] == id, 'score'] += 1


def top_5_related(business_data):
    # filter out business with very few review count
    business_data = business_data[business_data.distance < 10]
    business_data = business_data[business_data.review_count > 20]
    business_data = business_data[business_data.score > 10]
    business_data = business_data.sort_values('stars', ascending=False).head(5)
    business_data = business_data.sort_values('review_count', ascending=False)
    business_data = business_data.sort_values('score', ascending=False)
    business_data.index = np.arange(1, len(business_data) + 1)
    return business_data








