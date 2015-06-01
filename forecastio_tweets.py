import forecastio
import keys
from geopy.geocoders import GoogleV3
from datetime import datetime, timedelta

class TweetMaker:
    geocoder = None

    def __init__(self):
        self.geocoder = GoogleV3()

    def processMention(self, mention):
        user = mention['user']['screen_name']
        body = mention['text'].split()
        if len(body) < 3:
            return 'Hello, @'+user+'! Sorry, but I didn\'t understand your request.'

        zip = body[1]
        command = body[2]
        when = None
        if len(body) == 4:
            when = body[3]

        return self.makeTweet(user=user, zip=zip, cmd=command, when=when)

    def makeTweet(self, user, zip, cmd, when):
        cmd = cmd.lower()

        loc = self.getLatLong(zip)
        if loc is None:
            return 'Hello, @'+user+'! Your ZIP code was invalid, please try again.'
        current_time = self.getLocalTime(loc)

        if cmd == 'now':
            tweet = self.getCurrentSummary(user, loc, current_time)
        elif cmd == 'tomorrow':
            tweet = self.getFutureSummary(user, loc, current_time, days=1)
        elif cmd == 'days':
            try:
                when = int(when)
            except ValueError:
                return 'Hello, @'+user+'! Number of days was invalid, please try again.'
            tweet = self.getFutureSummary(user, loc, current_time, days=int(when))
        elif cmd == 'rain':
            day, hour = when.split('+')
            try:
                day, hour = int(day), int(hour)
            except ValueError:
                return 'Hello, @'+user+'! Time specification invalid, please try again.'
            tweet = self.getPrecipAtTime(user, loc, current_time, day, hour)
        elif cmd == 'temp':
            day, hour = when.split('+')
            try:
                day, hour = int(day), int(hour)
            except ValueError:
                return 'Hello, @'+user+'! Time specification invalid, please try again.'
            tweet = self.getTempAtTime(user, loc, current_time, day, hour)
        else:
            # TODO switch these back
            tweet = None
            #ret = 'Hello, @'+user+'! Sorry, but I didn\'t understand your request.'

        return tweet

    def getForecast(self, loc, time):
        return forecastio.load_forecast(keys.FORECAST_IO_KEY,
                                        lat=loc.latitude,
                                        lng=loc.longitude,
                                        time=time)

    def getCurrentSummary(self, user, loc, time):
        forecast = self.getForecast(loc, time)
        tweet = '@'+user+' '+str(forecast.currently().summary)
        return tweet[0:140]

    def getFutureSummary(self, user, loc, time, days):
        forecast = self.getForecast(loc, time+timedelta(days=days))
        tweet = '@'+user+' '+str(forecast.currently().summary)
        return tweet[0:140]

    def getTempAtTime(self, user, loc, time, days, hour):
        forecast = self.getForecast(loc, time+timedelta(days=days))
        out_time = str(self.formatTime(time, days, hour))
        tweet = '@'+user+' Temp for ' + out_time + ' is ' +str(forecast.hourly().data[hour].temperature)+' F'
        return tweet[0:140]

    def getPrecipAtTime(self, user, loc, time, days, hour):
        forecast = self.getForecast(loc, time+timedelta(days=days))
        precip_chance = int(float(forecast.hourly().data[hour].precipProbability) * 100)
        out_time = str(self.formatTime(time, days, hour))
        tweet = '@'+user+' Chance of Precipitation for ' + out_time + ' is ' + str(precip_chance)+'%'
        return tweet[0:140]

    def formatTime(self, current_time, days, hour):
        time = current_time+timedelta(days=days,hours=hour)
        fmt = '%a, %m/%d at %I:%M %p'
        return time.strftime(fmt)

    def getLatLong(self, zip):
        loc = self.geocoder.geocode(zip, exactly_one=True)
        # if an invalid zip was given, return None
        if loc is None:
            return None
        return loc

    def getLocalTime(self, loc):
        tz = self.geocoder.timezone((loc.latitude, loc.longitude))
        return datetime.now(tz)