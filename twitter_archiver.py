import datetime
import twitter_interface


DEFAULT_TIMESTAMP_FILE = "twitter_archiver_timestamp.txt"

def write_timestamp(handle=open(DEFAULT_TIMESTAMP_FILE, mode='w')):
    now = datetime.datetime.now()
    handle.write(now.stftime(twitter_interface.TIME_FORMAT))
    handle.close()
    
def get_timestamp(handle=open(DEFAULT_TIMESTAMP_FILE, mode='r')):
    ts = datetime.datetime.strptime(handle.read(), twitter_interface.TIME_FORMAT)
    handle.close()
    return ts

