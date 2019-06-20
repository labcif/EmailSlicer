import datetime

if __name__ == '__main__':
    now = datetime.datetime.now()
    print(now)
    delta = now - datetime.datetime.now()   # subtract time
    print(delta)
    print(now + delta)                      # add time
    print(dir(now))
    '''
        Year(YYYY)             |  %Y
        Month(MM)              |  %m
        Day (DD)               |  %d
        24 Hour (HH)           |  %H
        12 Hour (HH)           |  %I
        Minute (MM)            |  %M
        Secound (SS)           |  %S
        Microseconds (SSSSSS)  |  %f
        Timezone (Z)           |  %z
        AM/PM                  |  %p
        Day of the week        |  %A 
        Month of the year      |  %B
    '''
    epoch_timestamp = 874281600
    datetime_timestamp = datetime.datetime.utcfromtimestamp(epoch_timestamp)
    print(datetime_timestamp)
    print(datetime_timestamp.strftime('%A %B %d, %Y at %I:%M:%S %p'))
