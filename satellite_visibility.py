from skyfield.api import Topos, load, EarthSatellite
import pytz

def satellite_visibility(line1, line2, start_time, end_time, angle, latitude, longitude):
    # Observer's location
    if end_time <= start_time or not start_time or not end_time:
        return []
    observer = Topos(latitude_degrees=latitude, longitude_degrees=longitude)

    # Load timescale and satellite
    ts = load.timescale()
    satellite = EarthSatellite(line1, line2)

    # Find events
    t0 = ts.utc(start_time.year, start_time.month, start_time.day, start_time.hour, start_time.minute,
                start_time.second)
    t1 = ts.utc(end_time.year, end_time.month, end_time.day, end_time.hour, end_time.minute, end_time.second)
    times, events = satellite.find_events(observer, t0, t1, altitude_degrees=angle)

    # Process events into tuples
    passes = []
    pass_events = []
    for t, event in zip(times, events):
        pass_events.append(t.utc_datetime())
        if event == 2 and len(pass_events) == 3:  # set event
            passes.append((pass_events[0], pass_events[1], pass_events[2], satellite.model.satnum, True))
            pass_events = []
    tz = pytz.FixedOffset(0)
    if len(pass_events) == 2:
        passes.append((pass_events[0], pass_events[1], end_time.replace(tzinfo=tz), satellite.model.satnum))
    elif len(pass_events) == 1:
        passes.append((pass_events[0], end_time.replace(tzinfo=tz), satellite.model.satnum))
    return passes
