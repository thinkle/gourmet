"""
Generic parser for ISO 8601 duration strings.
See https://en.m.wikipedia.org/wiki/ISO_8601#Durations
These durations are used for cooktime and preptime in the schema.org format
https://schema.org/Recipe

Example:
seconds = isoduration_parser.parse_iso8601_duration(astring)
"""
import re
__all__ = ['parse_iso8601_duration']


def parse_iso8601_duration(duration):
    """Parse function for ISO 8601 durations.
    Although weeks, months or even years will be very unlikely
    for cooktime or preptime durations, this parser assumes:
    - one year has 365 days
    - one month has 30 days
    - one week has 7 days

    @param: duration - the ISO 8601 formatted duration string
    @ptype: string
    @return: seconds of duration
    @rtype: int
    @raises: ValueError on errors
    """
    if not duration:
        raise ValueError("invalid empty duration string %r" % duration)
    if not duration.startswith("P"):
        raise ValueError("duration string %r does not start with 'P'" % duration)
    if duration.startswith("PT"):
        # only hours, minutes and seconds
        seconds = parse_iso8601_duration_time(duration[2:])
    else:
        # this is unlikely for a recipe cooktime or preptime, but here we go
        if duration.endswith("W"):
            seconds = parse_iso8601_duration_week(duration[1:])
        else:
            # parse years, months, days
            seconds = parse_iso8601_duration_date(duration[1:])
    return seconds


def parse_iso8601_duration_time(duration):
    """Parse a duration time with hours, minutes and seconds.
    @param duration: string [n]H[n]M[n]S, where [n] is the number of hours, minutes or seconds; each part is optional
    @ptype duration: string
    @return: overall seconds of given time
    @rtype: int
    @raises: ValueError on errors
    """
    ro = re.compile(r"^((?P<hour>\d+)H)?" +
       r"((?P<minute>\d+)M)?" + 
       r"((?P<second>\d+)S)?$")
    match = ro.search(duration)
    if match:
        seconds = 0
        if match.group("second"):
            seconds += convert_to_positive_int(match.group("second"))
        if match.group("minute"):
            seconds += convert_to_positive_int(match.group("minute")) * 60
        if match.group("hour"):
            seconds += convert_to_positive_int(match.group("hour")) * 60 * 60
        return seconds
    raise ValueError("invalid duration time string %r" % duration)


def parse_iso8601_duration_week(duration):
    """Parse number of weeks of duration in format \d+W.
    @param duration: string [n]W, where [n] is the number of weeks
    @ptype duration: string
    @return: seconds of given weeks
    @rtype: int
    @raises: ValueError on errors
    """
    ro = re.compile(r"^(\d+)W")
    match = ro.search(duration)
    if match:
        s = match.group(1)
        weeks = convert_to_positive_int(s)
        return weeks * 7 * 24 * 60 * 60
    raise ValueError("invalid duration week string %r" % duration)


def parse_iso8601_duration_date(duration):
    """Parse number of years, months and days, and optional a time duration.
    @param duration: string [n]W, where [n] is the number of weeks
    @ptype duration: string
    @return: seconds of given date and time duration
    @rtype: int
    @raises: ValueError on errors
    """
    ro = re.compile(r"^((?P<year>\d+)Y)?" +
       r"((?P<month>\d+)M)?" + 
       r"((?P<day>\d+)D)?" +
       r"(T(?P<time>.*))?$")
    match = ro.search(duration)
    if match:
        seconds = 0
        if match.group("year"):
            seconds += convert_to_positive_int(match.group("year")) * 365 * 24 * 60 * 60
        if match.group("month"):
            seconds += convert_to_positive_int(match.group("month")) * 30 * 24 * 60 * 60
        if match.group("day"):
            seconds += convert_to_positive_int(match.group("day")) * 24 * 60 * 60
        if match.group("time"):
            seconds += parse_iso8601_duration_time(match.group("time"))
        return seconds
    raise ValueError("invalid duration date string %r" % duration)


def convert_to_positive_int(s):
    """Parse a given string to a positive int.
    @param s: the string to convert
    @ptype s: string
    @return: the parsed integer
    @rtype: int
    @raises: ValueError or OverflowError on number parsing errors or when the given number is not positive
    """
    num = int(s)
    if num < 0:
        raise ValueError("non-positive int parsed from %r" % s)
    return num


if __name__ == '__main__':
    print parse_iso8601_duration('PT40M')
