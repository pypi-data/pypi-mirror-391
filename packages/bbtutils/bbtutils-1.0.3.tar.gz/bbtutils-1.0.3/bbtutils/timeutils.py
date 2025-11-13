import pytz
import time
import datetime


def timestamp_to_local(timestamp, format = "%Y-%m-%d %H:%M:%S"):
    local_tz = pytz.timezone('Asia/Chongqing')
    local_dt = datetime.datetime.fromtimestamp(timestamp, local_tz)
    return local_dt.strftime(format)

def utc_to_timestamp(utc_time_str, utc_format='%Y-%m-%dT%H:%M:%SZ'):
    try:
        local_tz = pytz.timezone('Asia/Chongqing')
        local_format = "%Y-%m-%d %H:%M:%S"
        utc_dt = datetime.datetime.strptime(utc_time_str, utc_format)
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
        time_str = local_dt.strftime(local_format)
        return int(time.mktime(time.strptime(time_str, local_format)))
    except Exception as e:
        # print("warning utc_to_timestamp fail, try to use other format")
        if utc_format == '%Y-%m-%dT%H:%M:%SZ':
            return utc_to_timestamp(utc_time_str, utc_format='%Y-%m-%dT%H:%M:%S.%fZ')
        if utc_format == '%Y-%m-%dT%H:%M:%S.%fZ':
            return utc_to_timestamp(utc_time_str, utc_format='%Y-%m-%dT%H:%M:%SZ')
        raise e
 
def timestamp_to_utc(timestamp, utc_format='%Y-%m-%dT%H:%M:%SZ'):
    local_tz = pytz.timezone('Asia/Chongqing')
    local_format = "%Y-%m-%d %H:%M:%S"
    time_str = time.strftime(local_format, time.localtime(timestamp))
    dt = datetime.datetime.strptime(time_str, local_format)
    local_dt = local_tz.localize(dt, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt.strftime(utc_format)

