import re
from dndme.commands import Command
from dndme.gametime import Date


class AdjustDate(Command):

    keywords = ['date']
    help_text = """{keyword}
{divider}
Summary: Query, set, or adjust the in-game date using the calendar
specified at startup.

Usage:

    {keyword}
    {keyword} <day> <month> [<year>]
    {keyword} [+|-]<days>

Examples:

    {keyword}
    {keyword} 20 July
    {keyword} 20 July 1969
    {keyword} +7
    {keyword} -10
"""

    def get_suggestions(self, words):
        calendar = self.game.calendar
        if len(words) == 3:
            return [month['name']
                    for month in calendar.cal_data['months'].values()]

    def do_command(self, *args):
        calendar = self.game.calendar
        data = ' '.join(args)

        if not data:
            print(f"The date is {calendar}")
            return

        m_adjustment = re.match('([+-]\d+)', data)
        if m_adjustment:
            days = int(m_adjustment.groups()[0])
            calendar.adjust_date(days)
            print(f"The date is now {calendar}")
            self.game.changed = True
            return

        m_set = re.match('(\d+) (\w+) *(\d*)', data)
        if m_set:
            day, month, year = m_set.groups()
            day = int(day)
            year = int(year) if year else calendar.date.year

            calendar.set_date(Date(day, month, year))
            print(f"The date is now {calendar}")
            self.game.changed = True
            return

        print(f"Invalid date: {data}")