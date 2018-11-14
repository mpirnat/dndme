from dndme.commands import Command


class ShowSun(Command):

    keywords = ['sun', 'times']
    help_text = """{keyword}
{divider}
Summary: show the times of the day's notable solar events,
on the current date, at the current latitude.

Usage: {keyword}
    """

    def do_command(self, *args):
        almanac = self.game.almanac
        calendar = self.game.calendar
        latitude = self.game.latitude

        dawn, _ = almanac.dawn(calendar.date, latitude)
        sunrise, _ = almanac.sunrise(calendar.date, latitude)
        sunset, _ = almanac.sunset(calendar.date, latitude)
        dusk, _ = almanac.dusk(calendar.date, latitude)

        print(f"Dawn:    {dawn.hour:2}:{dawn.minute:02}")
        print(f"Sunrise: {sunrise.hour:2}:{sunrise.minute:02}")
        print(f"Sunset:  {sunset.hour:2}:{sunset.minute:02}")
        print(f"Dusk:    {dusk.hour:2}:{dusk.minute:02}")

        minutes_in_hour = calendar.cal_data['minutes_in_hour']
        sunrise_hours = sunrise.hour + (sunrise.minute / minutes_in_hour)
        sunset_hours = sunset.hour + (sunset.minute / minutes_in_hour)
        daylight_hours = int(sunset_hours - sunrise_hours)
        daylight_minutes = round((
                sunset_hours - sunrise_hours - daylight_hours) * \
                minutes_in_hour)

        print(f"Daylight: {daylight_hours} hours, {daylight_minutes} minutes")