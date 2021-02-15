# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 20:16:04 2021

@author: Enrique
"""



from downloader import download, guardar_imagen, elegir_trend, get_trends
import tweepy
import threading
import time
import sys

def on_new_client(api, trend):
    try:
        max_tweets=100
        
        estado = download(trend, api, max_tweets)
        if estado == True:
            time.sleep(10)
            guardar_imagen(trend, api)
    except Exception as e:
        print(e)
    finally:
        hilos.release()
        



#### Para simples busquedas publicas
TWITTER_APP_KEY=""

TWITTER_APP_SECRET=""
####

#### Para cuando tengamos que hacer cosas con nuestro usuario
TWITTER_KEY=""

TWITTER_SECRET=""
####

auth = tweepy.OAuthHandler(TWITTER_APP_KEY, TWITTER_APP_SECRET)
auth.set_access_token(TWITTER_KEY, TWITTER_SECRET)

api = tweepy.API(auth)
maxhilos = 5
hilos = threading.Semaphore(maxhilos)
usados_csv = "usados.csv"

    
while True:
    try:
        trends = get_trends(api)
        elegido = elegir_trend(trends, usados_csv)
        time.sleep(5)
        if(elegido != None):
            hilos.acquire()
            threading._start_new_thread(on_new_client,(api, elegido))
        else:
            print("Saliendo del servidor, no quedan trends")
            sys.exit()
            
    except KeyboardInterrupt:
        print("Gracefully shutting down the server!")
        sys.exit()
    except Exception as e:
        print(f"Well I did not anticipate this: {e}")
        sys.exit()
        
    
