# -*- coding: utf-8 -*-
"""
Created on Sat May  2 15:53:51 2020

@author: Gaurav
"""

#%% sentiment
from textblob import TextBlob

threshold = 0.1
pos_sentiments = 0
neg_sentiments = 0
with open('positive.txt') as f:
    pos_lines = f.readlines()
    for line in pos_lines:
        lineSentiment = TextBlob(line).sentiment[0]
        if lineSentiment > threshold:
            pos_sentiments += 1
with open('negative.txt') as f:
    neg_lines = f.readlines()
    for line in neg_lines:
        lineSentiment = TextBlob(line).sentiment[0]
        if lineSentiment < threshold:
            neg_sentiments += 1
print('positive sentiment accuracy: ', pos_sentiments/len(pos_lines))
print('negative sentiment accuracy: ', neg_sentiments/len(pos_lines))

#%% sqlite

import time
import sqlite3

conn = sqlite3.connect('tweets.db')
c = conn.cursor()

def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS sentiment(unix REAL, tweet TEXT, sentiment REAL)")
    conn.commit() 

create_table()
c.close()
conn.close()

#%%tweet
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
#from unidecode import unicode

#consumer key, consumer secret, access token, access secret. from twitter account
ckey="Rcz2AKAxnEBWUumIrT"
csecret="yhYc8k7zGZsG4a7IWPNdvP759sd8Z13YXp2PIVd"
atoken="945335158072229888-1QkQI1TYOgjKwMXNsYmoe"
asecret="LhIMj5wU4EKi0eU8kIDCAixk7mAdD6sT"

#create database
conn = sqlite3.connect('tweets.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS sentiment(unix REAL, tweet TEXT, sentiment REAL)")
conn.commit() 

class listener(StreamListener):
    num_data_points = 0
    def on_data(self, data):
        try:
            #load data
            data = json.loads(data)
            text = data['text']
            timestamp = data['timestamp_ms']
            sentiment = TextBlob(text).sentiment[0]
            
            #insert in database
            c.execute("INSERT INTO sentiment (unix, tweet, sentiment) VALUES (?, ?, ?)",
                      (timestamp, text, sentiment))
            conn.commit()
            #print number of added tweets
            self.num_data_points += 1
            print(self.num_data_points)
            
        except KeyboardInterrupt as e:
            print(str(e))
            c.close()
            conn.close()
        return True

    def on_error(self, status):
        print(status)

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

twitterStream = Stream(auth, listener())
twitterStream.filter(track=["car"])

#%% tweet without database
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
from unidecode import unidecode
from collections import deque
from textblob import TextBlob
import pandas as pd


class listener(StreamListener):
    num_data_points = 0
    
    maxlen = 100
    df_list = deque(maxlen=maxlen)
    def on_data(self, data):
        try:
            #load data
            data = json.loads(data)
            timestamp = data['timestamp_ms']
            text = unidecode(data['text'])
            sentiment = TextBlob(text).sentiment[0]
            self.df_list.append([timestamp, text, sentiment]) 
            listener.df = pd.DataFrame(list(self.df_list),columns=['timestamp', 'text', 'sentiment'])
            listener.df['sentiment_roll'] = listener.df['sentiment'].rolling(5).mean().dropna()
            #insert in database
            
            #print number of added tweets
            self.num_data_points += 1
            print(self.num_data_points)
            
        except KeyboardInterrupt as e:
            print(str(e))
        return True

    def on_error(self, status):
        print(status)


auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitterStream = Stream(auth, listener())
twitterStream.filter(track=['a', 'e', 'i', 'o', 'u'])

