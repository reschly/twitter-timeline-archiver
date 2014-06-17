#! /usr/bin/env python3

import re
import os
import sys
from twitter_interface import getTwitterByConfig, getTimelineData, getEmbed


DEFAULT_SINCEID_FILE = "twitter_archiver_sinceid.txt"

def write_sinceid(tweet_id, filename=DEFAULT_SINCEID_FILE):
    with open(filename, "w") as handle:
        handle.write(str(id))
    
def read_sinceid(filename=DEFAULT_SINCEID_FILE):
    try:
        with open(filename, "r") as handle:
            id_str = handle.read()
            return int(id_str)
    except FileNotFoundError:
        return 1
    
def new_tweet_data(since_id=1):
    tw = getTwitterByConfig()
    tweet_data = getTimelineData(tw, since_id=since_id)
    return tweet_data

def write_html_header(handle, title=b"Tweets"):
    header = b'<html><head><meta http-equiv="content-type" content="text/html; charset=UTF-8"><title>' + title + b'</title></head><body>\n<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>\n'
    handle.write(header)

def write_tweets(tweet_ids, handle):
    for tweet_id in tweet_ids:
        handle.write(getEmbed(tweet_id))

def write_html_trailer(handle):
    handle.write(b"</body></html>")

def read_tweets_from_html(filename):
    try:
        f = open(filename, 'rb')
    except FileNotFoundError:
        return []
    html = f.read()
    regex = re.compile("<blockquote.+?</blockquote>")
    tweets_html = regex.findall(str(html, 'utf-8'))
    f.close()
    return tweets_html

def append_tweets_to_html(tweet_data, filename, title=b"Tweets"):
    previous_tweets_html = read_tweets_from_html(filename)
    f = open(filename, 'wb')
    write_html_header(f, title)
    write_tweets(tweet_data, f)
    for html in previous_tweets_html:
        f.write(bytes(html, 'utf-8'))
        f.write(b"\n")
    write_html_trailer(f)
    f.close()


def get_filename(timestamp, directory):
    # make a file for each out of the day
    # filename format: YYYY_MM_DD_HH.html
    return os.path.join(directory, timestamp.strftime("%Y_%m_%d_%H.html"))

def get_title(timestamp):
    # Tuesday July 8 1500
    return timestamp.strftime("%A %B %d %H00")


def main(directory="."):
    since_id = read_sinceid()
    new_since_id = since_id
    tweet_data = new_tweet_data(since_id)
    tweets_by_hour = {}
    for (tweet_id, timestamp) in tweet_data:
        try:
            tweets_by_hour[get_filename(timestamp, directory)].append(tweet_id)
        except KeyError:
            tweets_by_hour[get_filename(timestamp, directory)] = [tweet_id]
        if tweet_id > new_since_id:
            new_since_id = tweet_id
    for filename in tweets_by_hour.keys():
        append_tweets_to_html(tweets_by_hour[filename], filename, bytes(filename, 'utf-8'))
    write_sinceid(new_since_id)
        
if __name__ == "__main__":
    dirname = "."
    if (len(sys.argv) == 2):
        dirname = sys.argv[1]
    main(dirname)
    