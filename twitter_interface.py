import twitter # sudo pip3 install twitter
import urllib
import json
import APIKEYS
import datetime
import os
                
''' MYCREDS.txt has the following format:
oauthtokenvalue
oauthsecretvalue
'''

TIME_FORMAT = "%a %b %d %H:%M:%S %z %Y"

def getTwitterByConfig(filename="MYCREDS.txt", path='.'):
    oauth_token, oauth_secret = twitter.read_token_file(os.path.join(path, filename))
    tw = twitter.Twitter(auth=twitter.OAuth(oauth_token, oauth_secret, APIKEYS.SPOKENTIMELINE_CONSUMERKEY, APIKEYS.SPOKENTIMELINE_CONSUMERSECRET))
    return tw

def printTweet(tweet):
    try:
        print(tweet['user']['screen_name'] + " at " + tweet['created_at'] + " tweeted " + tweet['text']);
    except UnicodeEncodeError:
        pass; #punt
    
def printTimeline(timeline):
    for tweet in timeline:
        printTweet(tweet)        

def getTweetData(tweet):
    timestamp = datetime.datetime.strptime(tweet["created_at"], TIME_FORMAT)
    return (tweet["id"], timestamp)

def getTimelineData(tw, since_id=1):
    return [getTweetData(tweet) for tweet in getTimeline(tw, since_id)]
        
def getTimeline(tw, count=200, since_id=1):
    return tw.statuses.home_timeline(count=count, since_id=since_id)

def getEmbed(tweet_id, path='.'):
    url = "https://api.twitter.com/1/statuses/oembed.json?id=" + str(tweet_id) + "&omit_script=true"
    response = urllib.request.urlopen(url, cafile=os.path.join(path, "cacert.pem"))
    # Next line feels wrong, but is the right way to do it: http://stackoverflow.com/a/6862922/535741
    json_data = json.loads(response.readall().decode('utf-8'))
    return json_data["html"].encode('utf-8')


if __name__ == "__main__":
    t = getTwitterByConfig()
    timeline = getTimeline(t)
    for tweet in timeline:
        (tweet_id, timestamp) = getTweetData(tweet)
        print(getEmbed(tweet_id))
