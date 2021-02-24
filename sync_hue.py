import json
import sys
from os import environ

from phue import Bridge

try:
    bridge = Bridge(environ['HUE_BRIDGE_HOST'], environ['HUE_BRIDGE_USERNAME'])
except:
    print('Set HUE_BRIDGE_HOST and HUE_BRIDGE_USERNAME environment variables!')
    sys.exit(1)

api_groups = bridge.get_group()

rooms = {}
for group_id, group_attributes in api_groups.items():
    if group_attributes['type'] == 'Room':
        rooms[group_id] = {
            'name': group_attributes['name'],
            'lights': group_attributes['lights']
        }

print(rooms)
