import tweepy
import time
import keys
from collections import deque
import pickle
import os
import json

class TweepyBot:
    bot = None  # holds tweepy instance
    stream = None  # holds stream endpoint for incoming mentions
    tweetFactory = None  # holds object that manufactures tweets
    lastMentionID = 0  # default value, overwritten on data load
    lastTweetTime = 1  # default value, overwritten on data load
    TIME_BETWEEN_TWEETS = 36  # seconds, based on maximum of 2400 tweets per day
    tweetQueue = deque()  # queue that holds tweets ready to be sent

    '''
    Initialize the Tweepy Bot
    '''
    def __init__(self, tweetFactory):
        auth = tweepy.OAuthHandler(keys.CONSUMER_KEY, keys.CONSUMER_SECRET)
        auth.set_access_token(keys.ACCESS_KEY, keys.ACCESS_SECRET)
        self.bot = tweepy.API(auth)
        self._loadData()
        self.tweetFactory = tweetFactory

    '''
    Get and process all mentions since the last time the bot was run
    '''
    def getMentions(self):
        # default count is 20, 200 is max according to twitter API documentation
        if self.lastMentionID == 0:
            mentions = self.bot.mentions_timeline(count=200)
        else:
            mentions = self.bot.mentions_timeline(count=200, since_id=self.lastMentionID)
        if mentions:
            if self.lastMentionID < mentions[0].id:
                self.setLastMentionID(mentions[0].id)
            for mention in mentions:
                self.processMention(mention._json)

    '''
    Process an individual mention, either from backlog or incoming stream
    '''
    def processMention(self, mention):
        tweet = self.tweetFactory.processMention(mention)
        if tweet is not None:
            self.addTweetToQueue(tweet)

    '''
    Place a tweet on the queue
    '''
    def addTweetToQueue(self, tweet):
        self.tweetQueue.append(tweet)

    '''
    Check if the queue of tweets is empty or not
    '''
    def tweetQueueNotEmpty(self):
        if self.tweetQueue:
            return True
        else:
            return False

    '''
    Pop a tweet off the queue and post to twitter
    '''
    def sendTweet(self):
        message = self.tweetQueue.popleft()
        print('Tweet: ' + message)
        self.bot.update_status(status=message)
        self._setTimeSinceTweet()

    '''
    Store last mention ID to variable
    '''
    def setLastMentionID(self, id):
        self.lastMentionID = id

    '''
    Store time in seconds since epoch of last tweet
    '''
    def _setTimeSinceTweet(self):
        self.lastTweetTime = time.time()

    '''
    Spamming defined by the constant TIME_BETWEEN_TWEETS, returns true when it's okay to tweet
    '''
    def notSpamming(self):
        return time.time() - self.TIME_BETWEEN_TWEETS > self.lastTweetTime

    '''
    Store persistent data using pickle to a binary file
    '''
    def _persistData(self):
        saved_data = {'last_id': self.lastMentionID, 'last_time': self.lastTweetTime, 'tweet_queue': self.tweetQueue}
        pickle.dump(saved_data, open(keys.PERSISTENCE_FILE, 'wb+'))

    '''
    Load persistent data
    '''
    def _loadData(self):
        if os.path.isfile(keys.PERSISTENCE_FILE):
            loaded_data = pickle.load(open(keys.PERSISTENCE_FILE, 'rb'))
            self.lastMentionID = loaded_data['last_id']
            self.timeSinceTweet = loaded_data['last_time']
            self.tweetQueue = loaded_data['tweet_queue']

    '''
    Start listening for new mentions on the stream end point
    '''
    def listenToStream(self):
        listener = StdOutListener()
        listener.addBotInstance(self)
        self.stream = tweepy.Stream(self.bot.auth, listener)
        self.stream.filter(track=['@'+keys.BOT_NAME], async=True)

    '''
    Save persistent data and disconnect the stream
    '''
    def shutdown(self):
        self._persistData()
        self.stream.disconnect()

"""
A listener handles tweets are the received from the stream end point.
This listener has a reference to the tweepybot that creates it so it can send incoming tweets to be processed
"""
class StdOutListener(tweepy.StreamListener):

    tbot = None

    def addBotInstance(self, tbot):
        self.tbot = tbot

    def on_data(self, data):
        try:
            decoded = json.loads(data)
            self.tbot.processMention(decoded)
            return True
        except:
            raise

    def on_error(self, status):
        print(status)
