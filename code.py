import time
import board
import alarm
import json

from adafruit_display_shapes.rect import Rect
from adafruit_magtag.magtag import MagTag

import hass_api

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

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

try:
    magtag.network.connect(max_attempts=3)
except OSError as err:
    # Put up some sort of error message instead of doing the rest of this stuff
    magtag.remove_all_text()
    magtag.add_text(
        text_font="/fonts/Arial-Bold-12.pcf",
        text_position=(10, (magtag.graphics.display.height // 2)-1),
        text=f'Failed to connect to wifi.\nWill retry again in 30 seconds')

    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic()+30000)
    alarm.exit_and_deep_sleep_until_alarms(time_alarm)

pool_data = hass_api.get_pool_data(magtag)

if not pool_data:
    print('Failed to get data from HASS: ', end='')

    if alarm.sleep_memory[0] != 0:
        print('Using cached data instead')
        mem = alarm.sleep_memory[0:]
        mem_str = mem.decode('utf-8').strip()
        pool_data = json.loads(mem_str)
        pool_data['updated'] = time.struct_time(pool_data['updated'])
    else:
        print('No cached data available, using blank data')
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

# Clear all of the current text from the screen, which should just
# be the start-up message.
print('clearing screen')
magtag.remove_all_text()

print('adding text')
# Build up the output screen with all of the data
magtag.add_text(
    text_font="/fonts/Arial-Bold-12.pcf",
    text_position=(10, 15),
    is_data=False
)
magtag.add_text(
    text_font="/fonts/Arial-Bold-12.pcf",
    text_position=(10, 35),
    is_data=False
)
magtag.add_text(
    text_font="/fonts/Arial-Bold-12.pcf",
    text_position=(10, 55),
    is_data=False
)
magtag.add_text(
    text_font="/fonts/Arial-Bold-12.pcf",
    text_position=(10, 75),
    is_data=False
)
print('setting text')

if pool_data.get('fountain', False):
    fountain = "On"
else:
    fountain = "Off"

when = pool_data.get('updated',None)
if when:
#    updated_at = f'{when.tm_mon : 2}/{when.tm_mday} {when.tm_hour}:{when.tm_min}:{when.tm_sec}'
    updated_at = f'{when.tm_mon:0>2}/{when.tm_mday:0>2} {when.tm_hour:0>2}:{when.tm_min:0>2}:{when.tm_sec:0>2}'
else:
    updated_at = 'unknown'
    
magtag.set_text(f"Pool: {pool_data.get('pool','unknown')}", 0, False);
magtag.set_text(f"Air: {pool_data.get('air','unknown')}", 1, False);
magtag.set_text(f"Water Feature: {fountain}", 2, False);
magtag.set_text(updated_at, 3, True)

print('save data')
# Store the data in the alarm cache so that it can be used again
# on the next refresh if we fail to connect to HASS.
pool_data['updated'] = list(pool_data['updated'])
data_mem = json.dumps(pool_data).encode('utf-8')
alarm.sleep_memory[0:len(data_mem)] = data_mem

print('sleeping')
magtag.peripherals.buttons[0].deinit()
magtag.peripherals.buttons[1].deinit()
a_alarm = alarm.pin.PinAlarm(pin=board.BUTTON_A, value=False, pull=True)
b_alarm = alarm.pin.PinAlarm(pin=board.BUTTON_B, value=False, pull=True)
#c_alarm = alarm.pin.PinAlarm(pin=board.BUTTON_C, value=False, pull=True)
#d_alarm = alarm.pin.PinAlarm(pin=board.BUTTON_D, value=False, pull=True)
time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic()+TIME_BETWEEN_REFRESHES)

alarm.exit_and_deep_sleep_until_alarms(a_alarm, b_alarm, time_alarm)#, c_alarm, d_alarm)
