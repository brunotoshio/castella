# Castella
Easy tweet searching using Twitter API

### Usage

```
git clone git@github.com:brunotoshio/castella.git

cd castella

pip install -r requirements.txt
```

Setup Twitter API accounts in the `accounts.yml`. More than one account can be added, ex:

```yaml
  accounts:
    - consumer_api_key: CONSUMER API KEY FOR ACCOUNT 1
      consumer_api_key_secret: CONSUMER API KEY SECRET FOR ACCOUNT 1
      access_token: ACCESS TOKEN FOR ACCOUNT 1
      access_token_secret: ACCESS TOKEN SECRET FOR ACCOUNT 1
    - consumer_api_key: CONSUMER API KEY FOR ACCOUNT 2
      consumer_api_key_secret: CONSUMER API KEY SECRET FOR ACCOUNT 2
      access_token: ACCESS TOKEN FOR ACCOUNT 2
      access_token_secret: ACCESS TOKEN SECRET FOR ACCOUNT 2
```

Change the `settings.yml` for your needs:

```yaml
settings:
  output:
    file: tweets.csv
    database:
      url: '127.0.0.1'
      port: 27017
      database: 'tweetdb'
      collection: 'tweets'
  search:
    query: 'any twitter query'
    params:
  interval:
    each: 'day'
    amount: 30
 ```
 
 The `output` defines the type of output (file or database or both), you can remove the `file` or `database` section if you are not going to use it.
 The current supported database is MongoDB (https://www.mongodb.com/).
 
 The `search` defines the search options. `query` is required and can be any query supported by Twitter standard operators (https://developer.twitter.com/en/docs/tweets/rules-and-filtering/overview/standard-operators.html).
 The `params` defines optional parameters. The list of all supported parameters is shown in https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets.html
 Ex:
 
 ```yaml
 ...
   search:
     query: 'any twitter query'
     params:
       locale: 'ja'
       geocode: '37.781157, -122.398720, 1mi'
 ...
 ```
 
 The `interval` defines the schedule of execution. 
 - `each` can be set to `day` or `week`.
 - `amount` defines how many executions.
 
 For example, to execute once each day during 30 days:
 ```yaml
 ...
   interval:
      each: 'day'
      amount: 30
 ...
 ```
 
