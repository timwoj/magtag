import time
import board
import alarm
import json
import displayio

from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from adafruit_magtag.magtag import MagTag

import hass_api

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Fonts for display of things
LABEL_FONT = bitmap_font.load_font('/fonts/Andika-Bold-Stripped-18.bdf')
DATE_FONT = bitmap_font.load_font('/fonts/Andika-Bold-Stripped-8.bdf')

# How frequently we should automatically update the screen in milliseconds
TIME_BETWEEN_REFRESHES = 15 * 60 * 1000

# magtag device instance
magtag = MagTag()

# Build up the display elements so that they can be turned on and off as we
# do the actual loading of data
pool_group = displayio.Group()
pool_labels = [label.Label(font=LABEL_FONT, text="Label: Value",
                           color=0x000000, anchor_point=(0, 0),
                           hidden=True) for _ in range(3)]

y_offset = 10
for lbl in pool_labels:
    lbl.anchored_position = (10, y_offset)
    y_offset += 25
    pool_group.append(lbl)

center_label = label.Label(LABEL_FONT, text='Refreshing from HomeAssistant...',
                           color=0x000000, anchor_point=(0, 0), hidden=True)
center_label.anchored_position = (10, (magtag.graphics.display.height // 2)-1)
center_label.hidden = True

date_battery_group = displayio.Group()
date_label = label.Label(DATE_FONT, text="A", color=0x000000,
                         anchor_point=(1, 0), hidden=True)
date_label.anchored_position = (magtag.graphics.display.width-5, 5)
date_battery_group.append(date_label)

battery_label = label.Label(DATE_FONT, text="A", color=0x000000,
                            anchor_point=(1, 0), hidden=True)
battery_label.anchored_position = (magtag.graphics.display.width-5, 15)
date_battery_group.append(battery_label)

magtag.splash.append(pool_group)
magtag.splash.append(center_label)
magtag.splash.append(date_battery_group)

def refresh_display():
    # refresh display
    time.sleep(magtag.display.time_to_refresh + 1)
    magtag.display.refresh()
    time.sleep(magtag.display.time_to_refresh + 1)

##### MAIN #####

# Try to connect to the network, but display an error message if it fails.
# try:
#     print('connecting to network')
#     magtag.network.connect(max_attempts=3)
#     print('success!')
# except OSError as err:
#     print('failed to connect')
#     center_label.text = "Failed to connect to wifi.\nWill retry again in 30 seconds."
#     center_label.hidden = False
#     refresh_display()

#     time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic()+30000)
#     alarm.exit_and_deep_sleep_until_alarms(time_alarm)

# print('getting local time')
# magtag.get_local_time()
# now = time.localtime()

# print('getting pool data')
# pool_data = hass_api.get_pool_data(magtag)

# if not pool_data:
#     print('Failed to get data from HASS: ', end='')

#     if alarm.sleep_memory[0] != 0:
#         print('Using cached data instead')
#         mem = alarm.sleep_memory[0:]
#         pool_data = json.loads(mem_str)
#         mem_str = mem.decode('utf-8').strip()
#         pool_data['updated'] = time.struct_time(pool_data['updated'])
#     else:
#         print('No cached data available, using blank data')
#         pool_data = {
#             'pool': 'unknown',
#             'air': 'unknown',
#             'fountain': False,
#             'updated': None
#         }
#     pool_data['conn_error'] = True
# else:
#     pool_data['conn_error'] = False

pool_data = {'fountain': False, 'air': '113 °F', 'conn_error': False, 'pool': '91 °F'}
pool_data['updated'] = time.struct_time((2022, 7, 19, 13, 46, 41, 1, 200, -1))
print(pool_data)

pool_labels[0].text = f"Pool: {pool_data.get('pool','unknown')}"
pool_labels[0].hidden = False
pool_labels[1].text = f"Air: {pool_data.get('air','unknown')}"
pool_labels[1].hidden = False

if pool_data.get('fountain', False):
    fountain = "On"
else:
    fountain = "Off"

pool_labels[2].text = f"Water Feature: {fountain}"
pool_labels[2].hidden = False

when = pool_data.get('updated',None)
if when:
#    updated_at = f'{when.tm_mon : 2}/{when.tm_mday} {when.tm_hour}:{when.tm_min}:{when.tm_sec}'
    updated_at = f'{when.tm_mon:0>2}/{when.tm_mday:0>2} {when.tm_hour:0>2}:{when.tm_min:0>2}:{when.tm_sec:0>2}'
else:
    updated_at = 'unknown'

date_label.text = updated_at
date_label.hidden = False

battery_label.text = f'Battery: {magtag.peripherals.battery}'
battery_label.hidden = False

refresh_display()

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
