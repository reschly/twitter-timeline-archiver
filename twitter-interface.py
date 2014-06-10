from twitter import * # sudo pip3 install twitter
import urllib
import json
import APIKEYS
import time
                
''' MYCREDS.txt has the following format:
oauthtokenvalue
oauthsecretvalue
'''

def getTwitterByConfig(filename="MYCREDS.txt"):
    oauth_token, oauth_secret = read_token_file(filename)
    twitter = Twitter(auth=OAuth(oauth_token, oauth_secret, APIKEYS.SPOKENTIMELINE_CONSUMERKEY, APIKEYS.SPOKENTIMELINE_CONSUMERSECRET))
    return twitter

def printTweet(tweet):
    try:
        print(tweet['user']['screen_name'] + " at " + tweet['created_at'] + " tweeted " + tweet['text']);
    except UnicodeEncodeError:
        pass; #punt
    
def printTimeline(timeline):
    for tweet in timeline:
        printTweet(tweet)        

def getTweetData(tweet):
    timestamp = time.strptime(tweet["created_at"], "%a %b %d %H:%M:%S %z %Y")
    return (tweet["id_str"], timestamp)

def getTimelineData(tw):
    return [getTweetData(tweet) for tweet in getTimeline(tw)]
        
def getTimeline(tw):
    return tw.statuses.home_timeline(count=200)

#def getEmbed(id_str):
#    url = "https://api.twitter.com/1/statuses/oembed.json?id=" + id_str
#    webcontent = urllib.request.urlopen(url)
#    json_data = json.loads(webcontent)
#    return json_data["html"]

if __name__ == "__main__":
    t = getTwitterByConfig()
    timeline = getTimeline(t)
    for tweet in timeline:
        print(getTweetData(tweet))