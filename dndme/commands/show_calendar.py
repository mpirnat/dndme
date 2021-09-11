import re
from dndme.commands import Command


class ShowCalendar(Command):

    keywords = ["calendar", "cal"]
    help_text = """{keyword}
{divider}
Summary: Show an overview of the calendar for the current year,
or a given year.

Usage:

    {keyword} [year]

Examples:

    {keyword}
    {keyword} 1488
"""

    def do_command(self, *args):
        calendar = self.game.calendar

        if args:
            try:
                year = int(args[0])
            except ValueError:
                print(f"Invalid year: {year}")
                return
        else:
            year = calendar.date.year

        self.print(f"<x1>{year}</x1>")
        print("-" * 60)
        for key, month in calendar.cal_data["months"].items():
            days_in_month = calendar.days_in_month(key, year)
            alt_name = f"\t{month.get('alt_name')}" if month.get("alt_name") else ""
            sdates = calendar.seasonal_dates_in_month(key)
            if sdates:
                if days_in_month > 1:
                    sdates = ", ".join(
                        [f"<x>{x['name']}:</x> {x['day']}" for x in sdates]
                    )
                else:
                    sdates = ", ".join([f"<x>{x['name']}</x>" for x in sdates])
            sdates = f"\t{sdates}" if sdates else ""

            if days_in_month == 0:
                continue
            elif days_in_month == 1:
                self.print(f"     <x>{month['name']:12}</x>{alt_name}{sdates}")
            else:
                self.print(
                    f"1-{days_in_month} <x>{month['name']:12}</x>{alt_name:25}{sdates}"
                )
