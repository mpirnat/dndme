from dndme.commands import Command

class Latitude(Command):

    keywords = ['latitude', 'lat']
    help_text = """{keyword}
{divider}
Summary: check or set the current latitude that will be used for calculating
the times for dawn, sunrise, sunset, and dusk.

Northern latitudes are specified in positive numbers, with southern latitudes
specified in negative numbers.

Usage: {keyword} [<latitude>]

Examples:

    {keyword}

    {keyword} 51

    {keyword} -45
    """

    def do_command(self, *args):
        if not args:
            print(f"The current latitude is {self.game.latitude}")
            return
        
        try:
            new_latitude = float(args[0])
            if new_latitude < -90 or new_latitude > 90:
                raise ValueError()
        except ValueError:
            print(f"Invalid latitude: {args[0]}")
            return
        
        self.game.latitude = new_latitude
        print(f"Okay; the latitude is now {new_latitude}")