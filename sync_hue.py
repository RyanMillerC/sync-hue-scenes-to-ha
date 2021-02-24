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

default_scene_names = [
    'Arctic aurora',
    'Bright',
    'Concentrate',
    'Dimmed',
    'Energize',
    'Nightlight',
    'Read',
    'Relax',
    'Savanna sunset',
    'Spring blossom',
    'Tropical twilight'
]

api_scenes = bridge.get_scene()

scenes = []
for scene_id, scene_attributes in api_scenes.items():
    scene_name = scene_attributes['name']
    if scene_name in default_scene_names:
        continue
    scene_type = scene_attributes['type']
    if scene_type == 'GroupScene':
        scene_group_id = scene_attributes['group']
        scene_room_name = rooms[scene_group_id]['name']
        scene = {
            'group_name': scene_room_name,
            'scene_name': scene_name
        }
        scenes.append(scene)
    elif scene_type == 'LightScene':
        lights = scene_attributes['lights']
        for room in rooms.values():
            if all(light in lights for light in room['lights']):
                scene = {
                    'group_name': room['name'],
                    'scene_name': scene_name
                }
                scenes.append(scene)

print(scenes)
