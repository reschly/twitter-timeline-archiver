#! /usr/bin/env python3

import datetime
import pytz
import re
from twitter_interface import getTwitterByConfig, getTimelineData, getEmbed, TIME_FORMAT


DEFAULT_TIMESTAMP_FILE = "twitter_archiver_timestamp.txt"

def write_timestamp(ts, filename=DEFAULT_TIMESTAMP_FILE):
    handle = open(filename, 'w')
    handle.write(ts.strftime(TIME_FORMAT))
    handle.close()
    
def get_timestamp(filename=DEFAULT_TIMESTAMP_FILE):
    try:
        handle = open(filename, 'r')
        ts = datetime.datetime.strptime(handle.read(), TIME_FORMAT)
        handle.close()
    except (FileNotFoundError, ValueError):
        ts = datetime.datetime.fromtimestamp(0, tz=pytz.utc)
    return ts    
    

def new_tweet_data(prev_timestamp):
    tw = getTwitterByConfig()
    tweet_data = getTimelineData(tw)
    return [(id_str, timestamp) for (id_str, timestamp) in tweet_data if (timestamp > prev_timestamp)]

def write_html_header(handle, title="Tweets"):
    header = '<html><head><title>%s</title></head><body>\n<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>\n' % (title,)
    handle.write(header)

def write_tweets(tweet_data, handle):
    for (id_str, timestamp) in tweet_data:
        try:
            handle.write(getEmbed(id_str))
        except UnicodeEncodeError:
            pass #punt

def write_html_trailer(handle):
    handle.write("</body></html>")

def read_tweets_from_html(filename):
    try:
        f = open(filename, 'r')
    except FileNotFoundError:
        return []
    html = f.read()
    regex = re.compile("<blockquote.+?</blockquote>")
    tweets_html = regex.findall(html)
    f.close()
    return tweets_html

def append_tweets_to_html(tweet_data, filename, title="Tweets"):
    previous_tweets_html = read_tweets_from_html(filename)
    f = open(filename, 'w')
    write_html_header(f, title)
    write_tweets(tweet_data, f)
    for html in previous_tweets_html:
        f.write(html)
        f.write("\n")
    write_html_trailer(f)
    f.close()


def get_filename(timestamp):
    # make a file for each out of the day
    # filename format: YYYY_MM_DD_HH.html
    return timestamp.strftime("%Y_%m_%d_%H.html")

def get_title(timestamp):
    # Tuesday July 8 1500
    return timestamp.strftime("%A %B %d %H00")

def main():
    prev_timestamp = get_timestamp()
    new_timestamp = prev_timestamp
    tweet_data = new_tweet_data(prev_timestamp)
    tweets_by_hour = {}
    for (id_str, timestamp) in tweet_data:
        try:
            tweets_by_hour[get_filename(timestamp)].append((id_str, timestamp))
        except KeyError:
            tweets_by_hour[get_filename(timestamp)] = [(id_str, timestamp)]
        if (timestamp > new_timestamp):
            new_timestamp = timestamp
    for hour in tweets_by_hour.keys():
        timestamp = tweets_by_hour[hour][0][1]
        append_tweets_to_html(tweets_by_hour[hour], get_filename(timestamp), get_title(timestamp))
    write_timestamp(timestamp)
        
if __name__ == "__main__":
    main()
    