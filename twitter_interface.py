import twitter # sudo pip3 install twitter
import urllib
import json
import APIKEYS
import datetime
                
''' MYCREDS.txt has the following format:
oauthtokenvalue
oauthsecretvalue
'''

TIME_FORMAT = "%a %b %d %H:%M:%S %z %Y"

def getTwitterByConfig(filename="MYCREDS.txt"):
    oauth_token, oauth_secret = twitter.read_token_file(filename)
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
    return (tweet["id_str"], timestamp)

def getTimelineData(tw):
    return [getTweetData(tweet) for tweet in getTimeline(tw)]
        
def getTimeline(tw, numtweets=200):
    return tw.statuses.home_timeline(count=numtweets)

def getEmbed(id_str):
    url = "https://api.twitter.com/1/statuses/oembed.json?id=" + id_str + "&omit_script=true"
    response = urllib.request.urlopen(url, cafile="cacert.pem")
    # Next line feels wrong, but is the right way to do it: http://stackoverflow.com/a/6862922/535741
    json_data = json.loads(response.readall().decode('utf-8'))
    return json_data["html"].encode('utf-8')


if __name__ == "__main__":
    t = getTwitterByConfig()
    timeline = getTimeline(t)
    for tweet in timeline:
        id_str, timestamp = getTweetData(tweet)
        print(getEmbed(id_str))
