# speech recognition library
import speech_recognition as sr
import pandas as pd
import numpy as np

from scipy.io import wavfile
from os import path
from gtts import gTTS
import os
import pyttsx3
import sys
import pgeocode
from geopy.distance import geodesic

import pymain

engine = pyttsx3.init()



print(sr.__version__)

# change this audio file
r = sr.Recognizer()
mic = sr.Microphone()

df_business = pd.read_csv("business.csv")
df_tip = pd.read_csv("tip.csv")
df_review = pd.read_csv("review.csv")

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




with mic as source:
    finito = False

    print("*At any moment you want to quit say done*")
    while not finito:
        engine.say("Please say your zip code")
        engine.runAndWait()
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        try:
            message = r.recognize_google(audio)
            print(message)

            if message == "done" :
                break

            confirm = "True"
            engine.say("Confirm zip code " + message)
            engine.runAndWait()

            audi = r.listen(source)
            confirm = r.recognize_google(audi)
            print("confirmed")

            if confirm == "no":
                continue

            zipcode = int(message)
            distance_calculator(zipcode)


            engine.say("What kind of restaurants do you want go?")
            engine.runAndWait()

            audio = r.listen(source)
            result = r.recognize_google(audio)

            list = result.split()
            restaurants = search_for_restaurant(list)
            top_five_restaurants = top_5_restaurant(restaurants)
            top_five_names = name_of_restaurant_list(top_five_restaurants)

            engine.say("The top five rated restaurants are")
            engine.runAndWait()

            engine.say(top_five_names)
            engine.runAndWait()
            print(top_five_names)

            engine.say(top_five_names[1])
            engine.runAndWait()
            engine.say(top_five_names[2])
            engine.runAndWait()
            engine.say(top_five_names[3])
            engine.runAndWait()
            engine.say(top_five_names[4])
            engine.runAndWait()
            engine.say("Please list your preference, one word at a time!")
            engine.runAndWait()

            audio = r.listen(source)
            result = r.recognize_google(audio)
            keywords = result.split()
            restaurant_relative(keywords, restaurants)
            top_related = top_5_related(restaurants)
            top_related_names = name_of_restaurant_list(top_related)
            engine.say("We have picked those restaurants for you based on your preference!")
            engine.runAndWait()

            engine.say(top_related_names[0])
            engine.runAndWait()

            engine.say(top_related_names[1])
            engine.runAndWait()
            engine.say(top_related_names[2])
            engine.runAndWait()
            engine.say(top_related_names[3])
            engine.runAndWait()
            engine.say(top_related_names[4])
            engine.runAndWait()
            quit = r.recognize_google(audio)

            if quit == "no":
                finito = True


        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))





    engine.say("Bye")

















# with sr.AudioFile(AUDIO_FILE) as source:
#     audio = r.record(source)
#     print(r.recognize_google(audio))




