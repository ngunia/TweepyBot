import forecastio
import keys
from geopy.geocoders import GoogleV3
from datetime import datetime, timedelta

class TweetMaker:
    geocoder = None

    def __init__(self):
        self.geocoder = GoogleV3()

    '''
    Break apart the mention into its key parts
    '''
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

    '''
    Call the appropriate construction method to make a tweet based on mention input
    '''
    def makeTweet(self, user, zip, cmd, when):
        cmd = cmd.lower()

        loc = self.getLatLong(zip)
        if loc is None:
            return 'Hello, @'+user+'! Your ZIP code was invalid, please try again.'
        current_time = self.getLocalTime(loc)
        print(self.formatTime(current_time))

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
            # TODO test an invalid when
            try:
                day, hour = when.split('+')
                day, hour = int(day), int(hour)
            except ValueError:
                return 'Hello, @'+user+'! Time specification invalid, please try again.'
            current_time = current_time.replace(hour=0,minute=0,second=0,microsecond=0)  # midnight of today
            tweet = self.getPrecipAtTime(user, loc, current_time, day, hour)
        elif cmd == 'temp':
            try:
                day, hour = when.split('+')
                day, hour = int(day), int(hour)
            except ValueError:
                return 'Hello, @'+user+'! Time specification invalid, please try again.'
            current_time = current_time.replace(hour=0,minute=0,second=0,microsecond=0)  # midnight of today
            tweet = self.getTempAtTime(user, loc, current_time, day, hour)
        else:
            tweet = 'Hello, @'+user+'! Sorry, but I didn\'t understand your request.'

        return tweet

    '''
    Get a forecast object at the desired time
    '''
    def getForecast(self, loc, time):
        return forecastio.load_forecast(keys.FORECAST_IO_KEY,
                                        lat=loc.latitude,
                                        lng=loc.longitude,
                                        time=time)

    '''
    Get the current forecast summary
    '''
    def getCurrentSummary(self, user, loc, time):
        # TODO add format time for the day
        forecast = self.getForecast(loc, time)
        tweet = '@'+user+' '+str(forecast.currently().summary)
        return tweet[0:140]

    '''
    Get a forecast summary for an upcoming day
    '''
    def getFutureSummary(self, user, loc, time, days):
        # TODO add format time for the day
        forecast = self.getForecast(loc, time+timedelta(days=days))
        tweet = '@'+user+' '+str(forecast.currently().summary)
        return tweet[0:140]

    '''
    Get the temperature at a given day/hour in deg F
    '''
    def getTempAtTime(self, user, loc, time, days, hour):
        forecast = self.getForecast(loc, time+timedelta(days=days))
        out_time = str(self.formatTime(time, days, hour))
        tweet = '@'+user+' Temp for ' + out_time + ' is ' +str(forecast.hourly().data[hour].temperature)+' F'
        return tweet[0:140]

    '''
    Get the probability of precipitation for a given day/hour in %
    '''
    def getPrecipAtTime(self, user, loc, time, days, hour):
        forecast = self.getForecast(loc, time+timedelta(days=days))
        precip_chance = int(float(forecast.hourly().data[hour].precipProbability) * 100)
        out_time = str(self.formatTime(time, days, hour))
        tweet = '@'+user+' Chance of Precipitation for ' + out_time + ' is ' + str(precip_chance)+'%'
        return tweet[0:140]

    '''
    Formats a datetime object for response
    '''
    def formatTime(self, current_time, days=0, hour=0):
        time = current_time+timedelta(days=days,hours=hour)
        fmt = '%a, %m/%d at %I:%M %p'
        return time.strftime(fmt)

    '''
    Returns the latitude and longitude for a given zip code, or None if invalid
    '''
    def getLatLong(self, zip):
        loc = self.geocoder.geocode(zip, exactly_one=True)
        # if an invalid zip was given, return None
        if loc is None:
            return None
        return loc

    '''
    Returns the local time based on latitude and longitude
    '''
    def getLocalTime(self, loc):
        tz = self.geocoder.timezone((loc.latitude, loc.longitude))
        return datetime.now(tz)