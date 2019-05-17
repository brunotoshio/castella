#!/usr/bin/env python
#-*- coding: utf-8 -*-

from ..account import AccountManager
import tweepy
import time


class TweetCrawler:
	def __init__(self):
		self.account_manager = AccountManager()
		self.current_account = None
		self.query = None
		self.query_params = dict(result_type="recent", include_entities=True, count=100)
		self.current_cursor = None
		self.last_max_id = -1

	## PUBLIC

	def search(self, query, handler, query_params = None):
		self.__set_search_params(query, query_params)
		self.current_cursor = self.__get_cursor()
		for status in self.__ratelimit_handled():
			self.last_max_id = status._json['id_str']
			if callable(handler):
				handler(status)

	## PRIVATE

	def __set_search_params(self, query, query_params):
		self.query = query
		if query_params is not None:
			self.query_params.update(query_params)

	def __get_tweepy_api(self):
		if self.current_account is None:
			self.__refresh_account()
		auth = tweepy.OAuthHandler(self.current_account.ckey, self.current_account.csecret)
		auth.set_access_token(self.current_account.akey, self.current_account.asecret)
		return tweepy.API(auth_handler=auth, timeout=60, retry_count=5, retry_delay=5, retry_errors=set([401, 404, 500, 503]))

	def __refresh_account(self, error = None):
		if self.current_account is None:
			self.current_account = self.account_manager.refresh_account()
			if self.current_account is None:
				time.sleep(15 * 60)
				self.__refresh_account()
		else:
			if error is None:
				self.current_account = self.account_manager.refresh_account(self.current_account)
			else:
				self.current_account = self.account_manager.refresh_account(self.current_account)

	def __get_cursor(self):
		api = self.__get_tweepy_api()
		if self.last_max_id == -1:
			return tweepy.Cursor(api.search, q=self.query, **self.query_params).items()
		else:
			return tweepy.Cursor(api.search, q=self.query, max_id=self.last_max_id, **self.query_params).items()

	def __ratelimit_handled(self):
		while True:
			try:
				yield self.current_cursor.next()
			except tweepy.TweepError as e:
				if "429" in e.reason:
					print("Rate Limit: ", self.current_account.username)
					print("Last id: ", self.last_max_id)
					self.__refresh_account()
					self.current_cursor = self.__get_cursor()
				else:
					print("An error has occurred: ", str(e))
					self.__refresh_account(str(e))
