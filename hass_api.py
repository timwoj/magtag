import time
import adafruit_requests

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print('Need to put some secrets in secrets.py')
    raise
    
hass_server = secrets.get('hass_server_ip_port', '')

# URLs to fetch from
POOL_TEMPERATURE = f'http://{hass_server}/api/states/sensor.pentair_15_a3_34_pool_temperature'
AIR_TEMPERATURE = f'http://{hass_server}/api/states/sensor.pentair_15_a3_34_air_temperature'
WATER_FEATURE = f'http://{hass_server}/api/states/switch.pentair_15_a3_34_water_feature'
LIGHT_FIXTURE = f'http://{hass_server}/api/states/light.pentair_15_a3_34_pool_light'

request_headers = { "Authorization": f"Bearer {secrets.get('hass_bearer_token','')}" }

def get_pool_data(requests, magtag):
    """Retrieve the data from HomeAssistant about what the pool is doing."""

    if not hass_server:
        return None
    
    try:
        response = requests.get(POOL_TEMPERATURE, headers=request_headers)
        pool_temp = f"{response.json().get('state', 0)} {response.json().get('attributes', {}).get('unit_of_measurement', '°F')}"

        response = requests.get(AIR_TEMPERATURE, headers=request_headers)
        air_temp = f"{response.json().get('state', 0)} {response.json().get('attributes', {}).get('unit_of_measurement', '°F')}"

        response = requests.get(WATER_FEATURE, headers=request_headers)
        fountain = f"{response.json().get('state', 'off')}" != "off"

        magtag.get_local_time()
        now = time.localtime()

        return {
            'pool': pool_temp,
            'air': air_temp,
            'fountain': fountain,
            'updated': now
        }

    except Exception as err:

        import traceback
        traceback.print_exception(err, err, err.__traceback__)
        return None

def change_fountain_state(requests):
    return

def change_light_state(requests):
    return
