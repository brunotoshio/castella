#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import requests
import time


class Account:
	def __init__(self):
		self.ckey = None
		self.csecret = None
		self.akey = None
		self.asecret = None
		self.last_expired = 0


class AccountManager:
	def __init__(self):
		self.__accounts = []

		with open("accounts.yml", "r") as stream:
			try:
				accounts = yaml.safe_load(stream)["accounts"]
				for account in accounts:
					new_account = Account()
					new_account.ckey = account['consumer_api_key']
					new_account.csecret = account['consumer_api_key_secret']
					new_account.akey = account['access_token']
					new_account.asecret = account['access_token_secret']
					self.__accounts.append(new_account)
			except Exception as err:
				print("Error: could not load accounts:", err)

	def refresh_account(self, current=None):
		if current is not None:
			current.last_expired = int(time.time())
		return self.__get_available_account()

	def __get_available_account(self):
		for account in self.__accounts:
			if account.last_expired == 0 or account.last_expired + 15 * 60 < int(time.time()):
				return account
		time.sleep(15 * 60)
		return self.__get_available_account()
