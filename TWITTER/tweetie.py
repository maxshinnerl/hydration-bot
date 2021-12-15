import tweepy
import os
from datetime import date

def loadkeys():
    """
    Load keys from bash profile
    """
    twitter_apikey = os.getenv("TWITTER_API_KEY")
    twitter_apisec = os.getenv("TWITTER_API_SECRET")
    twitter_accesskey = os.getenv("TWITTER_ACCESS_KEY")
    twitter_accesssec = os.getenv("TWITTER_ACCESS_SECRET")

    return (twitter_apikey, twitter_apisec, twitter_accesskey, twitter_accesssec)


def authenticate():
    """
    Get tuple of keys and connect
    """
    keys = loadkeys()

    auth = tweepy.OAuthHandler(keys[0], keys[1])
    auth.set_access_token(keys[2], keys[3])

    api = tweepy.API(auth, wait_on_rate_limit=True)
    
    return api

def is_today(status_date):
    """
    Pass in a twitter status.created_at.date() style date
    Return True if that's today
    False otherwise
    """
    if status_date == date.today():
        return True
    return False
    

def get_todays_di_tweets(api):
    """
    Pass in the API return from authenticate()
    Ideally this API is called only once in main.

    I think how I will structure this is that this function will
    just grab the last like 5 or 10 tweets, and just select
    anything from today's date containing the string "Xur"
    """

    name = "destinyinsights"

    tweets = []
    for status in tweepy.Cursor(api.user_timeline, tweet_mode = "extended", id=name).items(10):
        if is_today(status.created_at.date()):
            if ("Xur" in status.full_text) or \
               ("Banshee" in status.full_text) or \
               ("Ada-1" in status.full_text):
                
                text = status.full_text
                lines = ""
                for line in text.split("\n"):
                    if len(line) > 0:
                        if line[0] != "#":
                            lines += line + "\n"

                    else:
                        lines += "\n"

                tweets.append(lines)


    return tweets


if __name__ == "__main__":
    tweets = get_todays_di_tweets(authenticate())

    for tweet in tweets:
        print(tweet)
