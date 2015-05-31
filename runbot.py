from tweepybot import TweepyBot
import logging, keys, sys

# TODO add error checking for rate limits, program termination, exiting gracefully
# add error for double sending same request (twitter forbids identical tweets)

if keys.LOGGING:
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

if __name__ == '__main__':
    print('Starting bot..')
    try:
        bot = TweepyBot()
    except:
        # todo: make this better
        print('auth error')
        raise

    try:
        # add mentions since last run to queue
        bot.getMentions()

        # start listening for incoming mentions on stream endpoint
        print('Bot listening to stream! Use Ctrl+C to shutdown the bot.')
        bot.listenToStream()

        # check for tweets queued to go out and send them
        while True:
            # if there are ready to send tweets in the queue and rate limit isn't being exceeded, tweet one out
            if bot.tweetQueueNotEmpty() and bot.notSpamming():
                print('Bot sending a tweet..')
                bot.sendTweet()

    except KeyboardInterrupt:
        print('Keyboard interrupt detected, shutting down bot.')
        bot.shutdown()
        sys.exit(0) # TODO this doesn't work wtf
