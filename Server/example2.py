import time
import threading


def countdown(time_sec):
    while time_sec:
        # mins, secs = divmod(time_sec, 60)
        # timeformat = '{:02d}:{:02d}'.format(mins, secs)
        # print(timeformat, end='\r')
        time.sleep(1)
        time_sec -= 1

    print("stop")


tmr = threading.Thread(target=countdown, args=(5,))
tmr.start()
i = 0

while tmr.is_alive():
    print(i)
    i = i + 1
