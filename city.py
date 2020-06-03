import pyowm
import calendar
import datetime
from datetime import date

owm = pyowm.OWM('ecb7040454382ee36fdd354262f71db1')

triggers = ['rain', 'thunderstorm', 'tornado']

class City:
    
    #uses name to get weather data from open weather API
    def __init__(self, name):
        self.name = name

    def time(self, index):
        time = str(self.weather_list[index])[65:69]
        return time
    
    def date(self, index):
        date = str(self.weather_list[index])[55:63]
        return date
    
    def status(self, index):
        return self.weather_list[index].get_status()
    
    def detailed_status(self, index):
        return self.weather_list[index].get_detailed_status()
    
    #for every days forecast, append the day's date and the status to the current_statuses list
    def get_current_statuses(self):
        self.weather_list = []
        three_hr_forecast = owm.three_hours_forecast(self.name + ', US')
        forecast = three_hr_forecast.get_forecast()
        self.weather_list = forecast.get_weathers()
        current_statuses = []
        for index in range(0, len(self.weather_list)):
            status = self.detailed_status(index)
            current_statuses.append({self.date(index):status})
        return current_statuses
    
    #Get the statuses from today's forecast
    def todays_statuses(self, current_statuses):
        status_today = []
        
        #formatting the date so that it looks like the API's format, getting other time/date info ready
        todays_date = str(date.today())[2:len(str(date.today()))]
        today = todays_date[6:8]
        now = datetime.datetime.now()
        days_this_month = calendar.monthrange(now.year, now.month)[1]
        
        #technically just linear search, always 1 pair in status
        #building a list of next day weather statuses
        for status in current_statuses:
            for key in status:
                key_date = key[6:8]
                #getting next day forecast, if on the last day of month get the 1st's forecast, else get the current day + 1
                if (int(today) == days_this_month):
                    if key_date == '01':
                        status_today.append(status[key])
                elif int(key_date) == int(today) + 1:
                    status_today.append(status[key])
                    
        return status_today
    
    #determines whether or not it will rain/thunder/tornado
    def find_bad_weather(self):
        bad_weather = False
        
        curr = self.get_current_statuses()
        today = self.todays_statuses(curr)
        
        for status in today:
            # print(status)
            for trigger in triggers:
                if trigger in status:
                    bad_weather = True
        return bad_weather
    
    def test(self):
        today = str(date.today())
        today = today[2:len(today)]
        return today
    
        
    weather_list = []
    
    
        