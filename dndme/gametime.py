class Clock:
    
    def __init__(self, hours_in_day=24, minutes_in_hour=60, hour=0, minute=0):
        self.hours_in_day = hours_in_day
        self.minutes_in_hour = minutes_in_hour

        self.hour = hour
        self.minute = minute

    def __str__(self):
        return f"{self.hour:02}:{self.minute:02}"

    def adjust_time(self, hours=0, minutes=0):
        new_minute = (self.minute + minutes) % self.minutes_in_hour
        new_hour = (((self.hour + hours) + 
                     ((self.minute + minutes) // self.minutes_in_hour)) % 
                     self.hours_in_day)

        self.hour = new_hour
        self.minute = new_minute


class Calendar:

    def __init__(self, cal_data):
        self.cal_data = cal_data
        self.year = cal_data['default_year']
        self.month = cal_data['default_month']
        self.day = cal_data['default_day']

    def __str__(self):
        if self.days_in_month(self.month, self.year) > 1:
            return f"{self.day} {self.month} {self.year}"
        return f"{self.month} {self.year}"
    
    def days_in_month(self, month, year):
        month = month.lower()
        days = self.cal_data['months'][month]['days']
        if self.is_leap_year(year):
            return self.cal_data['months'][month].get('leap_year_days', days)
        return days
    
    def is_leap_year(self, year):
        leap_year_rule = self.cal_data.get('leap_year_rule')
        if not leap_year_rule:
            return False
        return eval(leap_year_rule.replace('year', str(year)))
    
    def set_date(self, day=None, month=None, year=None):
        # Allow changing any of the elements of the date
        day = day or self.day
        month = month or self.month
        year = year or self.year

        if not self._date_is_valid(day, month, year):
            return "lol nope"
        
        self.day = day
        self.month = month
        self.year = year
    
    def _date_is_valid(self, day, month, year):
        if month.lower() not in self.cal_data['months']:
            return False
        elif day < 1 or day > self.days_in_month(month, year):
            return False
        return True

    def adjust_date(self, days):
        month_keys = list(self.cal_data['months'].keys())

        if days > 0:   
            while (self.day + days) > self.days_in_month(self.month, self.year):
                # bleed off days to the end of the month
                days -= (self.days_in_month(self.month, self.year) - self.day)

                # move to the next month
                i = month_keys.index(self.month.lower())
                
                # advancing the month would roll over to next year
                if i+1 == len(month_keys):
                    i = -1
                    self.year += 1
                
                new_month = self.cal_data['months'][month_keys[i+1]]['name']

                self.month = new_month
                self.day = 0
            
            self.day += days

        elif days < 0:
            days = abs(days)
            while (self.day - days) < 1:
                # bleed off days to the beginning of the month
                days -= self.day

                # move to the previous month
                i = month_keys.index(self.month.lower())

                # going back a month would roll over to the prior year
                if i-1 < 0:
                    i = 0
                    self.year -= 1
                
                new_month = self.cal_data['months'][month_keys[i-1]]['name']

                self.month = new_month
                self.day = self.days_in_month(self.month, self.year)
            
            self.day -= days