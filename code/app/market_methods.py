import urllib2
import json
import py_compile
import datetime
import random
import time

QUERY = "http://localhost:8080/query?id={}"
ORDER = "http://localhost:8080/order?id={}&side=sell&qty={}&price={}"

def get_market_quote():
    try:
        quote = json.loads(urllib2.urlopen(QUERY.format(random.random())).read())
    except ValueError:
        print 'Failed to get quote from exchange'
        return -1
    return quote

def get_market_time():
    try:
        quote = json.loads(urllib2.urlopen(QUERY.format(random.random())).read())
    except ValueError:
        print 'Failed to get quote from exchange'
        return -1
    timestamp = quote['timestamp']
    t = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f");
    seconds = time.mktime(t.timetuple())
    return seconds

def get_end_of_day_time():
    try:
        quote = json.loads(urllib2.urlopen(QUERY.format(random.random())).read())
    except ValueError:
        print 'Failed to get quote from exchange'
        return -1

    timestamp = quote['timestamp']
    timestamp_modified = timestamp.split(" ")[0] + " 00:00:00.0"
    t = datetime.datetime.strptime(timestamp_modified, "%Y-%m-%d %H:%M:%S.%f");
    seconds = time.mktime(t.timetuple())
    seconds = seconds + (((8 * 60) + 30) * 60)
    return seconds

def get_market_time_formatted(format_str):
        time_seconds = get_market_time()
        time_str = datetime.datetime.fromtimestamp(time_seconds).strftime(format_str)
        return time_str

def get_market_price():
    try:
        quote = json.loads(urllib2.urlopen(QUERY.format(random.random())).read())
    except ValueError:
        print 'Failed to get quote from exchange'
        return -1
    price = float(quote['top_bid']['price'])
    return price
