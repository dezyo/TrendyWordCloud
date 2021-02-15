# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 15:38:05 2021

@author: Enrique
"""
import tweepy
import re
#import emoji
import string
import nltk
import csv
from wordcloud import WordCloud
import time
import operator


class StreamListener(tweepy.StreamListener):
    
    def __init__(self, trend, max_tweets):
        super(StreamListener, self).__init__()
        self.contador = 0
        self.trend=trend
        self.max_tweets=max_tweets
        self.list_cleaned=[]
    
    def on_status(self, status):
        if self.contador < self.max_tweets:
            if(hasattr(status, "retweeted_status")) == False:
                self.contador = self.contador + 1
                tweet=cleaner(status.text)
                tokens=tokenization(tweet)
                cleaned=remove_stopwords(tokens)
                self.list_cleaned.append(cleaned)
                print(self.contador, self.trend, cleaned)
                
        else:
            print("abriendo trend_{}.csv en on_status".format(self.trend))
            with open('csv/trend_{}.csv'.format(self.trend), 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(self.list_cleaned)
                
            return False

    def on_error(self, status_code):
        if status_code == 420:
            print("Error 420 en {}".format(self.trend))
            print("Esperando 15 minutos")
            time.sleep(900)
            return False
        
def cleaner(tweet):
    tweet = tweet.lower()
    tweet = re.sub(r"(?:\@|http?\://|https?\://|www)\S+", "", tweet) #Remove http links
    #tweet = ''.join(c for c in tweet if c not in emoji.UNICODE_EMOJI) #Remove Emojis
    tweet = "".join([char for char in tweet if char not in string.punctuation])
    tweet = re.sub('[0-9]+', '', tweet)
    tweet = re.sub("@[A-Za-z0-9]+","",tweet) #Remove @ sign
    tweet = " ".join(tweet.split())
    tweet = tweet.replace("#", "").replace("_", " ") #Remove hashtag sign but keep the text
    return tweet

def tokenization(text):
    text = re.split('\W+', text)
    return text

def remove_stopwords(text):
    stopword = nltk.corpus.stopwords.words('spanish')
    text = [word for word in text if word not in stopword]
    return text
       

def download(trend, api, max_tweets):
    try:
        stream_listener = StreamListener(trend, max_tweets)
        stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
        stream.filter(track=[trend], languages=["es"])
        return True
    except Exception as e:
        print(e)
        return False

     
def guardar_imagen(trend, api):
    tweets=[]
    print("abriendo trend_{}.csv en guardar_imagen".format(trend))
    with open('csv/trend_{}.csv'.format(trend), newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            tweet=' '.join(row)
            tweets.append(tweet)
            
    wordcloud = WordCloud(width=1600, height=800, max_words=500,background_color="white").generate(" ".join([tw for tw in tweets]))
    wordcloud.to_file("img/trend_{}.png".format(trend))
    print("Imagen guardada correctamente: img/trend_{}.png".format(trend))
    print("Tweeteando trend: {}".format(trend))
    tweet_img("img/trend_{}.png".format(trend), trend, api)

def get_trends(api):
    SPAIN_WOE_ID = 23424950
    
    trends = api.trends_place(SPAIN_WOE_ID) #trends de españa
    trends = trends[0]
    trends = trends["trends"]
    
    dict_trends={}
    
    for trend in trends:
        if trend["promoted_content"]==None and trend["tweet_volume"]!= None:
            dict_trends[trend["name"].upper()] = trend["tweet_volume"]
    
    list_trends_raw = sorted(dict_trends.items(), key=operator.itemgetter(1), reverse=True)
    list_trends = []
    
    for trend in list_trends_raw:
        list_trends.append(trend[0])
        
    return list_trends

def elegir_trend(trends, usados_csv):
    lista_usados = []
    elegido = None
    with open(usados_csv, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            lista_usados.append(row)
                
    for trend in trends:
        if [trend] not in lista_usados:
            print(trend)
            elegido=trend
            break
        
    if elegido != None:
        with open(usados_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([elegido])
    
    return elegido

def tweet_img(img, trend, api):
    api.update_with_media(img, status=trend)
    return True