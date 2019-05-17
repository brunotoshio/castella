import pymongo
import yaml
import sched
import time
import json
from castella import TweetCrawler


class Castella(object):
    def __init__(self):
        # Get connection parameters
        with open("settings.yml", "r") as stream:
            try:
                settings = yaml.safe_load(stream)["settings"]

                # Database
                self.server_url = settings["output"]["database"]["url"]
                self.server_port = settings["output"]["database"]["port"]
                self.database_name = settings["output"]["database"]["database"]
                self.collection_name = settings["output"]["database"]["collection"]

                # Search
                self.query = settings["search"]["query"]
                self.search_params = settings["search"]["params"]

                # Schedule
                self.interval_type = settings["interval"]["each"]
                self.interval_amount = settings["interval"]["amount"]
                self.total_executions = 0
            except yaml.YAMLError as exc:
                print("ERROR: No settings.yml found or it could not be read")

    def execute_search(self):
        # Mongo connection
        client = pymongo.MongoClient(self.server_url, self.server_port)
        db = client[self.database_name]
        self.tweets = db[self.collection_name]

        self._create_scheduled_executions()

    def _save_tweet(self, tweet):
        print("Saving: ", tweet._json["id_str"])
        try:
            bson = tweet._json
            bson["query_str"] = self.query
            self.tweets.insert_one(bson)
        except:
            print("Error occurred when trying to save")
    
    def _search(self):
        # Continue from last id
        try:
            self.tweets.create_index([("id", pymongo.DESCENDING)])
            last_tweet = self.tweets.find({}).sort([("id", pymongo.DESCENDING)]).next()
        except StopIteration:
            last_tweet = None

        # Searching
        tc = TweetCrawler()
        params = dict(result_type="recent", include_entities=True, count=100)
        if isinstance(self.search_params, dict):
            params.update(self.search_params)
        if last_tweet is not None:
            print("============================================================")
            print("Resuming from tweet id:", last_tweet['id_str'])
            print("============================================================")
            params["since_id"] = last_tweet.get("id_str")
        tc.search(self.query, self._save_tweet, params)

        self.total_executions += 1
        print("============================================================")
        print("Finished for today...")
        print(self.total_executions, "out of", self.interval_amount, "scheduled executions")
        print("============================================================")
        if self.total_executions < self.interval_amount:
            print("Keep this process running until the execution of the last scheduled iteration, or stop this process to cancel further executions.")
            print("============================================================")
        


    # Preparing functions for scheduler
    def _days(self):
        return time.time() / (60 * 60 * 24)


    def _weeks(self):
        return time.time() / (60 * 60 * 24 * 7)

    # Scheduling events
    def _create_scheduled_executions(self):
        if self.interval_type == "day":
            handler = self._days
        else:
            handler = self._weeks
        scheduler = sched.scheduler(handler, time.sleep)

        for i in range(self.interval_amount):
            scheduler.enter(i, 1, self._search)
        scheduler.run()

if __name__ == "__main__":
    searcher = Castella()
    searcher.execute_search()