import datetime


def isDuringThatTime(startTime, endTime):
    start_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + startTime, '%Y-%m-%d%H:%M')
    end_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + endTime, '%Y-%m-%d%H:%M')
    now_time = datetime.datetime.now()
    if start_time < now_time < end_time:
        return True
    return False
