#! /usr/bin/env python3

import re
import os
import datetime
import pytz # sudo pip3 install pytz
import argparse
from twitter_interface import getTwitterByConfig, getTimelineData, getEmbed, TIME_FORMAT


DEFAULT_SINCEID_FILE = "twitter_archiver_sinceid.txt"
DEFAULT_TIMESTAMP_FILE = "twitter_archiver_timestamp.txt"

def write_timestamp(ts, filename=DEFAULT_TIMESTAMP_FILE):
    with open(filename, 'w') as handle:
        handle.write(ts.strftime(TIME_FORMAT))
        
def read_timestamp(filename=DEFAULT_TIMESTAMP_FILE):
    try:
        handle = open(filename, 'r')
        ts = datetime.datetime.strptime(handle.read(), TIME_FORMAT)
        handle.close()
    except (IOError, ValueError):
        ts = datetime.datetime.fromtimestamp(0, tz=pytz.utc)
    return ts 

def write_sinceid(tweet_id, filename=DEFAULT_SINCEID_FILE):
    with open(filename, "w") as handle:
        handle.write(str(tweet_id))
    
def read_sinceid(filename=DEFAULT_SINCEID_FILE):
    try:
        with open(filename, "r") as handle:
            id_str = handle.read()
            return int(id_str)
    except IOError:
        return 1
    
def new_tweet_data(since_id=1, path='.'):
    tw = getTwitterByConfig(path=path)
    tweet_data = getTimelineData(tw, since_id=since_id)
    return tweet_data

def write_html_header(handle, title=b"Tweets"):
    header = b'<html><head><meta http-equiv="content-type" content="text/html; charset=UTF-8"><title>' + title + b'</title></head><body>\n<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>\n'
    handle.write(header)

def write_tweets(tweet_ids, handle, path):
    for tweet_id in tweet_ids:
        handle.write(getEmbed(tweet_id, path))

def write_html_trailer(handle):
    handle.write(b"</body></html>")

def read_tweets_from_html(filename):
    try:
        f = open(filename, 'rb')
    except IOError:
        return []
    html = f.read()
    regex = re.compile("<blockquote.+?</blockquote>")
    tweets_html = regex.findall(str(html, 'utf-8'))
    f.close()
    return tweets_html

def append_tweets_to_html(tweet_data, filename, title=b"Tweets", path="."):
    previous_tweets_html = read_tweets_from_html(filename)
    f = open(filename, 'wb')
    write_html_header(f, title)
    write_tweets(tweet_data, f, path)
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

def cleanup(dirname):
    # Remove logs that are more than 30 days old
    # Chmod everything else to rw-r--r-- / 644
    for filename in os.listdir(dirname):
        if not os.path.isfile(filename):
            pass
        # get timestamp from filename
        # format = YYYY_MM_DD_HH.html
        name_parts = filename.split("_")
        if len(name_parts) != 4:
            continue
        if not (name_parts[3].endswith(".html")):
            continue
        year = int(name_parts[0])
        month = int(name_parts[1])
        day = int(name_parts[2])
        file_time = datetime.datetime(year=year, month=month, day=day)
        now = datetime.datetime.now()
        if (now - file_time) > datetime.timedelta(days=30):
            os.remove(os.path.join(dirname, filename))
        else:
            os.chmod(os.path.join(dirname, filename), 0o644) #python3
        


def main(pathdir, outdir):
    since_id = read_sinceid(os.path.join(pathdir, DEFAULT_SINCEID_FILE))
    prev_timestamp = read_timestamp(os.path.join(pathdir, DEFAULT_TIMESTAMP_FILE))
    new_since_id = since_id
    new_timestamp = prev_timestamp
    tweet_data = new_tweet_data(since_id, pathdir)
    tweets_by_hour = {}
    for (tweet_id, timestamp) in tweet_data:
        if (timestamp < prev_timestamp):
            continue # it appears that home_timeline may returns tweets prior to the given since_id
        try:
            tweets_by_hour[get_filename(timestamp, outdir)].append(tweet_id)
        except KeyError:
            tweets_by_hour[get_filename(timestamp, outdir)] = [tweet_id]
        if tweet_id > new_since_id:
            new_since_id = tweet_id
        if timestamp > new_timestamp:
            new_timestamp = timestamp
    for filename in tweets_by_hour.keys():
        append_tweets_to_html(tweets_by_hour[filename], filename, path=pathdir)
    write_sinceid(new_since_id, filename=os.path.join(pathdir, DEFAULT_SINCEID_FILE))
    write_timestamp(new_timestamp, filename=os.path.join(pathdir, DEFAULT_TIMESTAMP_FILE))
    cleanup(outdir)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', type=str, default='.',
                   help='path to program directory ("/home/user/twitter-timeline-archiver")')
    parser.add_argument('-o', '--output', type=str, default='.',
                   help='path to write outputs to ("/var/www/tweets")')
    args = parser.parse_args()
    main(args.path, args.output)