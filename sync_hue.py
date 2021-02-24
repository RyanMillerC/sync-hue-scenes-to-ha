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

api_scenes = bridge.get_scene()

scenes = {}
for scene_id, scene_attributes in api_scenes.items():
    scene_name = scene_attributes['name']
    scene_type = scene_attributes['type']
    if scene_type == 'GroupScene':
        scene_group_id = scene_attributes['group']
        scene_room_name = rooms[scene_group_id]
        print(f'{scene_name}:{scene_room_name}')
    elif scene_type == 'LightScene':
        print(f'Skipping {scene_name} because it is a LightScene')
