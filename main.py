import pymongo
import yaml
import sched
import time
from castella import TweetCrawler


# Get connection parameters
with open("settings.yml", "r") as stream:
    try:
        settings = yaml.load(stream)["settings"]

        # File
        filename = settings["output"]["file"]

        # Database
        server_url = settings["output"]["database"]["url"]
        server_port = settings["output"]["database"]["port"]
        database_name = settings["output"]["database"]["database"]
        collection_name = settings["output"]["database"]["collection"]

        # Search
        query = settings["search"]["query"]
        search_params = settings["search"]["params"]

        # Schedule
        interval_type = settings["interval"]["each"]
        interval_amount = settings["interval"]["amount"]
    except yaml.YAMLError as exc:
        print("ERROR: No settings.yml found or it could not be read")


# Mongo connection
client = pymongo.MongoClient(server_url, server_port)
db = client[database_name]
tweets = db[collection_name]


# Insert Handler
def save_tweet(tweet):
    bson = tweet._json
    bson["query_str"] = query
    print("Saving: ", bson["id_str"])
    tweets.insert_one(bson)


def search():
    # Continue from last id
    try:
        tweets.create_index([("id", pymongo.DESCENDING)])
        last_tweet = tweets.find({}).sort([("id", pymongo.DESCENDING)]).next()
    except StopIteration:
        last_tweet = None

    # Searching
    tc = TweetCrawler()
    params = dict(result_type="recent", include_entities=True, count=100)
    if isinstance(search_params, dict):
        params.update(search_params)
    if last_tweet is not None:
        print(last_tweet)
        params["since_id"] = last_tweet.get("id_str")
        print(params)

    print(params)
    tc.search(query, save_tweet, params)


# Preparing functions for scheduler
def days():
    return time.time() / (60 * 60 * 24)


def weeks():
    return time.time() / (60 * 60 * 24 * 7)


# Creating scheduler
if interval_type == "day":
    handler = days
else:
    handler = weeks
scheduler = sched.scheduler(handler, time.sleep)


# Scheduling events
for i in range(interval_amount):
    scheduler.enter(i, 1, search)
scheduler.run()
