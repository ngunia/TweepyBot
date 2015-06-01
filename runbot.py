from tweepybot import TweepyBot
import forecastio_tweets
import logging, keys, sys
from tweepy import TweepError

if keys.LOGGING:
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

try:
    # create bot instance by passing in a tweet factory
    bot = TweepyBot(forecastio_tweets.TweetMaker())

    # add mentions since last run to queue
    print('Bot processing any mentions since last run..')
    bot.getMentions()

    # start listening for incoming mentions on stream endpoint
    print('Bot listening to stream! Use Ctrl+C to shutdown the bot.')
    bot.listenToStream()

    # check tweet queue
    while True:
        # if there are ready to send tweets in the queue and rate limit isn't being exceeded, tweet one out
        if bot.tweetQueueNotEmpty() and bot.notSpamming():
            print('Bot sending a tweet..')
            try:
                bot.sendTweet()
                print()
            except TweepError as e:
                if str(e) == 'Twitter error response: status code = 403':
                    print('Error: Can\'t send duplicate tweet. Not sending above, continuing.')
                    print()
                    continue
                else:
                    raise

except KeyboardInterrupt:
    print('Keyboard interrupt detected, shutting down bot..')
    bot.shutdown()
    print('Goodbye!')
    sys.exit()
