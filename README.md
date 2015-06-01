TODO: fix the formatting of this

Bot Interactions:

Bot Twitter handle: @forecastcheck

Basic request format:

@forecastcheck \<zip\> \<cmd\> \<when\>


Day summary:

@forecastcheck \<zip\> \<cmd\> \<when\>

@forecastcheck \<zip\> now

@forecastcheck \<zip\> tomorrow

@forecastcheck \<zip\> days \<int num days in future\>



Precipitation chance:

@forecastcheck \<zip\> rain \<int days in future 0-8\>+\<int hour of day on 0-23\>

Temperature at given hour:

@forecastcheck \<zip\> temp \<int days in future 0-8\>+\<int hour of day on 0-23\>



To run code:

Dependencies:

pip install tweepy

pip install python-forecastio

pip install geopy

pip install pytz



At the terminal: python3 runbot.py
