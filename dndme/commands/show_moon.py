import re
from dndme.commands import Command
from dndme.gametime import Date

class ShowMoon(Command):

    keywords = ['moon', 'moons']
    help_text = """{keyword}
{divider}
Summary: show the current phases of all moons, or the phases of all moons
on a specific date.

Usage: {keyword} [<date>]

Examples:

    moon
    moon 1 Hammer 1488
    """

    def do_command(self, *args):
        almanac = self.game.almanac
        calendar = self.game.calendar
        latitude = self.game.latitude

        date = None
        data = ' '.join(args)

        if not data:
            date = calendar.date
        else:
            m_date = re.match('(\d+) (\w+) *(\d*)', data)
            if m_date:
                date = Date(
                        int(m_date.groups()[0]),
                        m_date.groups()[1],
                        int(m_date.groups()[2] or calendar.date.year))
        
        if date:
            for moon_key, moon_info in calendar.cal_data['moons'].items():
                phase, _ = almanac.moon_phase(moon_key, date)
                print(f"{moon_info['name']}: {phase}")
            return
        
        print(f"Invalid date: {data}")