from observatory_visibility import observatory_visibility
from satellite_visibility import satellite_visibility
from process_overlaps import process_overlaps
import pytz
from skyfield.api import EarthSatellite

def generate_plan(observatories, satellites, start_time_plan, end_time_plan, plan_timezone_offset, event_type_plan):
    plan = []
    obs_time = []
    for obs in observatories:
        start_time = obs['START_TIME']
        end_time = obs['END_TIME']
        tz = []
        if obs['TIMEZONE_OFFSET']:
            tz = pytz.FixedOffset(60 * obs['TIMEZONE_OFFSET'])
        else:
            tz = pytz.FixedOffset(0)
        start_time = start_time.replace(tzinfo=tz)
        end_time = end_time.replace(tzinfo=tz)
        obs_time.append([(start_time, end_time)])

    sat_time = []
    start_time_sat = start_time_plan
    end_time_sat = end_time_plan
    tzp = []
    if plan_timezone_offset:
        tzp = pytz.FixedOffset(60 * plan_timezone_offset)
    else:
        tzp = pytz.FixedOffset(0)
    start_time_sat = start_time_sat.replace(tzinfo=tzp)
    end_time_sat = end_time_sat.replace(tzinfo=tzp)
    for sat in satellites:
        sat_time.append([(start_time_sat, end_time_sat)])
    # print(obs_time)

    for time_range_sat_orig, sat in zip(sat_time, satellites):
        plan_sat = []
        for time_range_obs_orig, obs in zip(obs_time, observatories):
            time_range_obs = time_range_obs_orig.copy()
            time_range_sat = time_range_sat_orig.copy()
            ov = observatory_visibility(obs['START_TIME'], obs['END_TIME'], obs['LATITUDE'], obs['LONGITUDE'],
                                        obs['TIMEZONE_OFFSET'], event_type_plan)  # check observatory visibility times
            ovv = []  # observatory_visibility_verified
            # print(ov)
            for time_frame in ov:  # look for overlaps of visibility and available observatory time (verified)
                # print(time_frame)
                if time_frame:
                    process_overlaps(time_frame, time_range_obs, ovv)

            ovvv = []
            for time_frame in ovv:  # look for overlaps of visibility and available satellite time (verified, twice)
                if time_frame:
                    process_overlaps(time_frame, time_range_sat, ovvv)

            ps = []  # passes
            for tf in ovvv:  # look for passes of satellite above coordinates in available verified timeframes
                pl = satellite_visibility(sat['TLE_LINE1'], sat['TLE_LINE2'], tf[0], tf[1], obs['ANGLE'],
                                          obs['LATITUDE'], obs['LONGITUDE'])
                if pl:
                    for pass_ in pl:  # for now, append start and end times
                        if len(pass_) in {5, 4}:
                            ps.append((pass_[0], pass_[2]))
                        elif len(pass_) == 3:
                            ps.append((pass_[0], pass_[1]))

            end_passes1 = []
            end_passes2 = []

            for pass_ in ps:
                if pass_:
                    process_overlaps(pass_, time_range_sat_orig, end_passes1)
                    process_overlaps(pass_, time_range_obs_orig, end_passes2)
            plan_sat.append((end_passes1, obs["COMMENT"]))
        tsat = EarthSatellite(sat['TLE_LINE1'], sat['TLE_LINE2'])
        plan.append((plan_sat, tsat.model.satnum_str))
    return plan
