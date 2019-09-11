import datetime


def get_epoch_unix_time(date_time):
    epoch = datetime.datetime.utcfromtimestamp(0)

    try:
        date_epoch = (date_time - epoch).total_seconds()
    except:
        date_epoch = 'NULL'
    finally:
        return date_epoch


def get_date_time(date_epoch):
    try:
        date_time = datetime.datetime.fromtimestamp(
            date_epoch).strftime('%Y-%m-%d %H:%M:%S')  # .strftime('%c')
    except:
        date_time = 'NULL'
    finally:
        return date_time
