import sys
import time

# from telemetrix_uno_r4.minima.telemetrix_uno_r4_minima import telemetrix_uno_r4_minima
from telemetrix import telemetrix

# create a telemetrix instance
board = telemetrix.Telemetrix()

# some defined values
INPUT_PIN = 12
LED_PIN = 6

# index values to dereference the callback data
CB_PIN_MODE = 0
CB_PIN = 1
CB_VALUE = 2
CB_TIME = 3

# variable to hold the last time a button state changed
debounce_time = time.time()


def the_callback(data):
    """
    A callback function to report data changes.
    This will print the pin number, its reported value and
    the date and time when the change occurred

    :param data: [pin, current reported value, pin_mode, timestamp]
    """

    global debounce_time

    print(data)

    # if the time from the last event change is > .2 seconds, the input is debounced
    if data[CB_TIME] - debounce_time > .3:
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[CB_TIME]))
        print(f'Pin: {data[CB_PIN]} Value: {data[CB_VALUE]} Time Stamp: {date}')
        debounce_time = data[CB_TIME]

        # set output pin to the state reported by the server
        if data[CB_VALUE] == 1:
            board.digital_write(LED_PIN, 1)
        else:
            board.digital_write(LED_PIN, 0)


def setup():
    """
    Configure the board for use.
    """

    # set the input pin and register the callback
    board.set_pin_mode_digital_input(INPUT_PIN, the_callback)

    # set the output pin
    board.set_pin_mode_digital_output(LED_PIN)


def loop():
    """
    Loop forever until user enters Control C
    """
    try:
        time.sleep(.001)
    except:
        if KeyboardInterrupt:
            board.shutdown()
            sys.exit(0)


# set up the program
setup()
# loop forever
while True:
    loop()
