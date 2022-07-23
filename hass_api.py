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
STATES_URL = f'{hass_api_url}/states'
POOL_TEMPERATURE = f'{hass_api_url}/states/sensor.pentair_15_a3_34_pool_temperature'
AIR_TEMPERATURE = f'{hass_api_url}/states/sensor.pentair_15_a3_34_air_temperature'
WATER_FEATURE = f'{hass_api_url}/states/switch.pentair_15_a3_34_water_feature'
LIGHT_FIXTURE = f'{hass_api_url}/states/light.pentair_15_a3_34_pool_light'
AUTOMATION_URL = f'{hass_api_url}/services/automation/trigger'

request_headers = {"Authorization": f"Bearer {secrets.get('hass_bearer_token','')}",
                   "Content-Type": "application/json"}

def get_pool_data(magtag):
    """Retrieve the data from HomeAssistant about what the pool is doing."""

    hass_data = {
        'pool': 'Unknown',
        'air': 'Unknown',
        'fountain': False,
        'light': False
    }

    try:
        response = magtag.network.fetch(STATES_URL, headers=request_headers)
        data = response.json()

        pool_temp_data = [x for x in data if x['entity_id'] == 'sensor.pentair_15_a3_34_pool_temperature']
        if pool_temp_data:
            d = pool_temp_data[0]
            hass_data['pool'] = f"{d.get('state', 0)} {d.get('attributes', {}).get('unit_of_measurement', '°F')}"

        air_temp_data = [x for x in data if x['entity_id'] == 'sensor.pentair_15_a3_34_air_temperature']
        if air_temp_data:
            d = air_temp_data[0]
            hass_data['air'] = f"{d.get('state', 0)} {d.get('attributes', {}).get('unit_of_measurement', '°F')}"

        fountain_data = [x for x in data if x['entity_id'] == 'sensor.pentair_15_a3_34_pool_temperature']
        if fountain_data:
            d = fountain_data[0]
            if d.get('state','off') == 'Off':
                hass_data['fountain'] = 'Off'
            else:
                hass_data['fountain'] = 'On'

        light_data = [x for x in data if x['entity_id'] == 'sensor.pentair_15_a3_34_pool_temperature']
        if light_data:
            d = light_data[0]
            if d.get('state','off') == 'Off':
                hass_data['light'] = 'Off'
            else:
                hass_data['light'] = 'On'

        now = time.localtime()

        hass_data['updated'] = time.localtime()
        return hass_data

    except Exception as err:

        import traceback
        traceback.print_exception(err, err, err.__traceback__)
        return None

def change_fountain_state(magtag):
    try:
        print('changing fountain state')
        payload = {"entity_id": "automation.pool_fountain_toggle"}
        response = magtag.network.fetch(AUTOMATION_URL, headers=request_headers, payload=payload)
    except Exception as err:

        import traceback
        traceback.print_exception(err, err, err.__traceback__)

def change_light_state(magtag):
    try:
        print('changing light state')
        payload = {"entity_id": "automation.pool_light_toggle"}
        response = magtag.network.fetch(AUTOMATION_URL, headers=request_headers, payload=payload)
    except Exception as err:

        import traceback
        traceback.print_exception(err, err, err.__traceback__)
