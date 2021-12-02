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


def createfunc():
    global is_ready
    is_ready = False
    time.sleep(1)


def continuefunction():
    global is_ready
    while not is_ready:
        pass
        # print("corriendo")


tmr2 = threading.Thread(target=createfunc, args=())
print(tmr2.is_alive())
tmr2.start()
print(tmr2.is_alive())
tmr = threading.Thread(target=continuefunction, args=())
tmr.start()

time.sleep(1)
is_ready = True
