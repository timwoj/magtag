import ipaddress
import ssl
import socketpool
import time
import board
import alarm
import json
import io
import sys
import wifi

import adafruit_requests
from adafruit_display_shapes.rect import Rect
from adafruit_magtag.magtag import MagTag

import hass_api

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

def try_refresh(magtag):
    """Attempt to refresh the display. Catch 'refresh too soon' error
    and retry after waiting 10 seconds.
    """
    try:
        magtag.refresh()
    except RuntimeError as too_soon_error:
        # catch refresh too soon
        print(too_soon_error)
        print("waiting before retry refresh()")
        time.sleep(10)
        magtag.refresh()

# How frequently we should automatically update the screen in milliseconds
TIME_BETWEEN_REFRESHES = 15 * 60 * 1000

# magtag device instance
magtag = MagTag()

# Put up some sort of error message instead of doing the rest of this stuff
magtag.add_text(
    text_font="/fonts/Arial-Bold-12.pcf",
    text_position=(10, (magtag.graphics.display.height // 2)-1),
)
magtag.set_text(f'Refreshing from HomeAssistant...')
try_refresh(magtag)

# Connect to the wifi, build a socket pool out of the connection, and
# setup a requests instance to make http requests against it. Depending
# on how long the magtag's been asleep, this might have to reconnect.
attempts = 1
requests = None
while attempts < 3:
    try:
        wifi.radio.connect(ssid=secrets.get('ssid','unknown-ssid'),
                           password=secrets.get('password','unknown-password'))

        pool = socketpool.SocketPool(wifi.radio)
        requests = adafruit_requests.Session(pool)
        break
    except Exception as err:
        import traceback
        traceback.print_exception(err, err, err.__traceback__)
        print('Failed to connect to wifi')
        time.sleep(10)
        attempts += 1
        
if not requests:

    magtag.remove_all_text()

    # Put up some sort of error message instead of doing the rest of this stuff
    magtag.add_text(
        text_font="/fonts/Arial-Bold-12.pcf",
        text_position=(10, 15),
    )
    magtag.set_text(f'Failed to connect to wifi, will retry again in 30 seconds')
    try_refresh(magtag)

    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic()+30000)
    alarm.exit_and_deep_sleep_until_alarms(time_alarm)

pool_data = hass_api.get_pool_data(requests, magtag)
print(pool_data)
if not pool_data:
    if alarm.sleep_memory[0] != 0:
        mem = alarm.sleep_memory[0:]
        print(mem)
        mem_str = mem.decode('utf-8').strip()
        print(mem_str)
        pool_data = json.loads(mem_str)
        pool_data['updated'] = time.struct_time(pool_data['updated'])
    else:
        pool_data = {
            'pool': 'unknown',
            'air': 'unknown',
            'fountain': False,
            'updated': None
        }
    pool_data['conn_error'] = True
else:
    pool_data['conn_error'] = False

print(pool_data)

magtag.remove_all_text()

magtag.add_text(
    text_font="/fonts/Arial-Bold-12.pcf",
    text_position=(10, 15),
)
magtag.set_text(f"Pool: {pool_data.get('pool','unknown')}", 0, 0);

magtag.add_text(
    text_font="/fonts/Arial-Bold-12.pcf",
    text_position=(10, 35),
)
magtag.set_text(f"Air: {pool_data.get('air','unknown')}", 1, 0);

if pool_data.get('fountain', False):
    fountain = "On"
else:
    fountain = "Off"

magtag.add_text(
    text_font="/fonts/Arial-Bold-12.pcf",
    text_position=(10, 55),
)
magtag.set_text(f"Water Feature: {fountain}", 2, 0);

when = pool_data.get('updated',None)
if when:
    updated_at = f'{when.tm_mon}/{when.tm_mday} {when.tm_hour}:{when.tm_min}:{when.tm_sec}'
else:
    updated_at = 'unknown'
magtag.add_text(
    text_font="/fonts/Arial-Bold-12.pcf",
    text_position=(10, 75),
)
magtag.set_text(updated_at, 3, True)

# if pool_data.get('conn_error', False):
#     magtag.set_text('Failed to retrieve data!', 4, True)

try_refresh(magtag)

pool_data['updated'] = list(pool_data['updated'])
data_mem = json.dumps(pool_data).encode('utf-8')
alarm.sleep_memory[0:len(data_mem)] = data_mem

magtag.peripherals.buttons[0].deinit()
magtag.peripherals.buttons[1].deinit()
a_alarm = alarm.pin.PinAlarm(pin=board.BUTTON_A, value=False, pull=True)
b_alarm = alarm.pin.PinAlarm(pin=board.BUTTON_B, value=False, pull=True)
#c_alarm = alarm.pin.PinAlarm(pin=board.BUTTON_C, value=False, pull=True)
#d_alarm = alarm.pin.PinAlarm(pin=board.BUTTON_D, value=False, pull=True)
time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic()+TIME_BETWEEN_REFRESHES)

alarm.exit_and_deep_sleep_until_alarms(a_alarm, b_alarm, time_alarm)#, c_alarm, d_alarm)
