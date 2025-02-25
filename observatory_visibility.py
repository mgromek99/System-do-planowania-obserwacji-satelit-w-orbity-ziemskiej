import datetime as dt
from skyfield import almanac
from skyfield.api import wgs84, load


def observatory_visibility(start_time, end_time, latitude, longitude, timezone_offset, event_type):
    #tz = dt.timezone(dt.timedelta(hours=timezone_offset))

    if end_time <= start_time:
        return []

    # Skyfield setup
    ts = load.timescale()

    # Create a timezone object
    tz = dt.timezone(dt.timedelta(hours=timezone_offset))

    # Replace the tzinfo for start and end times
    start_time = start_time.replace(tzinfo=tz)
    end_time = end_time.replace(tzinfo=tz)

    t0 = ts.from_datetime(start_time)
    t1 = ts.from_datetime(end_time)
    eph = load('de421.bsp')
    location = wgs84.latlon(latitude, longitude)
    f = almanac.dark_twilight_day(eph, location)
    times, events = almanac.find_discrete(t0, t1, f)

    observation_times = []
    observation_time_start = []
    test_t0 = previous_e = f(t0).item()

    if test_t0 < event_type:
        observation_time_start = start_time

    for t, e in zip(times, events):
        t_atz = t.astimezone(tz)
        if e == event_type:
            if previous_e >= e:
                observation_time_start = t_atz
        elif previous_e == event_type:
            if previous_e < e:
                observation_times.append((observation_time_start, t_atz))
                observation_time_start = []
        previous_e = e

    if observation_time_start:
        observation_times.append((observation_time_start, end_time))
    return observation_times
