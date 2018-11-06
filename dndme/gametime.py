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
        print(self)