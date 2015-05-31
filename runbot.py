import tweepy
import time
import keys
import queue
import pickle
import os
import json
from forecastio_tweets import TweetMaker

class TweepyBot:
    bot = None
    stream = None
    tweetFactory = None
    lastMentionID = 0
    lastTweetTime = 1
    TIME_BETWEEN_TWEETS = 36  # seconds, based on maximum of 2400 tweets per day
    tweetQueue = queue.Queue()

    def __init__(self):
        auth = tweepy.OAuthHandler(keys.CONSUMER_KEY, keys.CONSUMER_SECRET)
        auth.set_access_token(keys.ACCESS_KEY, keys.ACCESS_SECRET)
        self.bot = tweepy.API(auth)
        self._loadData()
        self.tweetFactory = TweetMaker()

    def getMentions(self):
        # default count is 20, 200 is max according to twitter API documentation
        mentions = self.bot.mentions_timeline(count=200, since_id=self.lastMentionID)
        if mentions:
            self.setLastMentionID(mentions[0].id)
            self._persistData()
            self.processMentions(mentions)

    def processMentions(self, mentions):
        for mention in mentions:
            user = mention.user.screen_name
            body = mention.text.split()
            if len(body) < 3:
                continue
            command = body[1]
            word = body[2]
            self.generateTweet(user=user, word=word, cmd=command)

    def addTweetToQueue(self, tweet):
        self.tweetQueue.put(tweet)

    def tweetQueueNotEmpty(self):
        return not self.tweetQueue.empty()

    def generateTweet(self, user, word, cmd):
        tweet = self.tweetFactory.makeTweet(user=user, word=word, cmd=cmd)
        if tweet is not None:
            self.addTweetToQueue(tweet)

    def sendTweet(self):
        message = self.tweetQueue.get()
        print('Tweet: ' + message)
        self.bot.update_status(status=message)
        self._setTimeSinceTweet()

    def setLastMentionID(self, id):
        self.lastMentionID = id

    def _setTimeSinceTweet(self):
        self.lastTweetTime = time.time()

    def notSpamming(self):
        return time.time() - self.TIME_BETWEEN_TWEETS > self.lastTweetTime

    def _persistData(self):
        saved_data = {'last_id': self.lastMentionID, 'last_time': self.lastTweetTime}
        pickle.dump(saved_data, open(keys.PERSISTENCE_FILE, 'wb'))

    def _loadData(self):
        # TODO save tweet queue
        if os.path.isfile(keys.PERSISTENCE_FILE):
            loaded_data = pickle.load(open(keys.PERSISTENCE_FILE, 'rb'))
            self.lastMentionID = loaded_data['last_id']
            self.timeSinceTweet = loaded_data['last_time']

    def listenToStream(self):
        # TODO load tweet queue
        listener = StdOutListener()
        listener.addBotInstance(self)
        self.stream = tweepy.Stream(self.bot.auth, listener)
        self.stream.filter(track=['@'+keys.BOT_NAME], async=True)

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
            self.tbot.setLastMentionID(decoded['id'])
            self.processMention(decoded)
            # TODO REMOVE THIS LINE
            self.tbot._persistData()
            return True
        except:
            raise

    def processMention(self, mention):
        print(mention)
        loc = None
        if mention['user']['location']:
            loc = mention['user']['location']
        print(mention['user']['geo_enabled'])
        if str(mention['user']['geo_enabled']) == 'True' and mention['user']['coordinates'] is not None:
            loc = mention['user']['coordinates']

        user = mention['user']['screen_name']
        body = mention['text'].split()
        if len(body) < 3:
            return
        command = body[1]
        word = body[2]

        self.tbot.generateTweet(user=user, word=word, cmd=command, loc=loc)

    def on_error(self, status):
        print(status)
