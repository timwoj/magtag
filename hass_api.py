import time

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print('Need to put some secrets in secrets.py')
    raise
    
hass_api_url = secrets.get('hass_api_url', '')
if not hass_api_url:
    raise ImportError('Missing hass_api_url in secrets')

# URLs to fetch from
POOL_TEMPERATURE = f'{hass_api_url}/sensor.pentair_15_a3_34_pool_temperature'
AIR_TEMPERATURE = f'{hass_api_url}/sensor.pentair_15_a3_34_air_temperature'
WATER_FEATURE = f'{hass_api_url}/switch.pentair_15_a3_34_water_feature'
LIGHT_FIXTURE = f'{hass_api_url}/light.pentair_15_a3_34_pool_light'

request_headers = { "Authorization": f"Bearer {secrets.get('hass_bearer_token','')}" }

def get_pool_data(magtag):
    """Retrieve the data from HomeAssistant about what the pool is doing."""

    try:
        response = magtag.network.fetch(POOL_TEMPERATURE, headers=request_headers)
        pool_temp = f"{response.json().get('state', 0)} {response.json().get('attributes', {}).get('unit_of_measurement', '°F')}"
        print('')

        response = magtag.network.fetch(AIR_TEMPERATURE, headers=request_headers)
        air_temp = f"{response.json().get('state', 0)} {response.json().get('attributes', {}).get('unit_of_measurement', '°F')}"
        print('')

        response = magtag.network.fetch(WATER_FEATURE, headers=request_headers)
        fountain = f"{response.json().get('state', 'off')}" != "off"
        print('')

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

def change_fountain_state(magtag):
    return

def change_light_state(magtag):
    return
