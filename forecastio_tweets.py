import forecastio

class TweetMaker:

    def makeTweet(self, user, word, cmd, loc=None):
        ret = None
        cmd = cmd.lower()

        if cmd == 'def':
            ret = self._makeTweetDefinition(user, word)
        elif cmd == 'syn':
            ret = self._makeTweetAntonyms(user, word)
        elif cmd == 'ant':
            ret = self._makeTweetSynonyms(user, word)
        else:
            ret = None
            #ret = 'Hello, @'+user+'! Sorry, but I didn\'t understand your request..'

        return ret

    def _makeTweetDefinition(self, user, word):
        # use dict API, add to queue
        tweet = '@'+user+' def of ' + word
        return tweet

    def _makeTweetSynonyms(self, user, word):
        tweet = '@'+user+' syns of ' + word
        return tweet

    def _makeTweetAntonyms(self, user, word):
        tweet = '@'+user+' ants of ' + word
        return tweet
