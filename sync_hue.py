"""
# Sync Philips Hue Scenes to Home Assistant

This script will sync scenes from Philips Hue into Home Assistant (HA).

Because of how Hue scenes are designed, they can only be set by HA and
not read. This means they can not be imported or used like HA scenes.

Instead, this script will add an HA script entity for each Hue scene. The
scripts will call a given Hue scene when activated in HA.

This script requires that your Hue Bridge information be set in
environment variables. Replace contents in '<>' with your info.

```bash
export HUE_BRIDGE_HOST='<IP of Hue bridge>'
export HUE_BRIDGE_USERNAME='<Username/token for Hue bridge auth>'
```
"""


import glob
import json
import os
import sys
import yaml

from phue import Bridge


try:
    bridge = Bridge(
        os.environ['HUE_BRIDGE_HOST'],
        os.environ['HUE_BRIDGE_USERNAME']
    )
except:
    print('Set HUE_BRIDGE_HOST and HUE_BRIDGE_USERNAME environment variables!')
    sys.exit(1)


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


def main():
    """Execute rest of script."""
    remove_existing_scripts()
    rooms = get_rooms()
    scenes = get_scenes()
    mapped_scenes = map_scenes_to_rooms(scenes, rooms)
    for group_name, scene_name in mapped_scenes:
        create_yaml(group_name, scene_name)


def remove_existing_scripts():
    """Remove existing scripts from previous run."""
    existing_scripts = glob.glob('./scripts/hue_scene_*.yaml')
    for script in existing_scripts:
        os.remove(script)


def get_rooms():
    """Get groups of type 'Room' from Hue API.

    :returns: group_id, name, and lights of each room
    :rtype: dict
    """
    rooms = {}
    api_groups = bridge.get_group()
    for group_id, group_attributes in api_groups.items():
        if group_attributes['type'] == 'Room':
            rooms[group_id] = group_attributes
    return rooms


def get_scenes():
    """Get scenes from the Hue API.

    Will ignore all default Hue scenes.

    :returns:
    :rtype: list
    """
    scenes = {}
    api_scenes = bridge.get_scene()
    for scene_id, scene_attributes in api_scenes.items():
        scene_name = scene_attributes['name']
        if scene_name in default_scene_names:
            continue
        scenes[scene_id] = scene_attributes
    return scenes


def map_scenes_to_rooms(scenes, rooms):
    """Map scenes to their respective rooms.

    GroupScenes are a simple mapping by group ID. LightScenes must be
    determined by mapping lights in the scene to lights in a group
    (room). If all lights in a scene belong to a given group (room),
    that room is used for the mapping.

    :param dict scenes:
        Scenes from Hue API
    :param dict rooms:
        Groups of type 'Room' from Hue API

    :returns: group_name and scene_name tuple of each match
    :rtype: list
    """
    mapped_scenes = []
    for scene in scenes.values():
        scene_name = scene['name']
        scene_type = scene['type']
        if scene_type == 'GroupScene':
            scene_group_id = scene['group']
            mapped_scenes.append((rooms[scene_group_id]['name'], scene_name))
        elif scene_type == 'LightScene':
            scene_lights = scene['lights']
            for room in rooms.values():
                if all(light in scene_lights for light in room['lights']):
                    mapped_scenes.append((room['name'], scene_name))
    return mapped_scenes


def create_yaml(group_name, scene_name):
    """Create Home Assistant ready YAML scripts.

    :param str group_name:
        Name of group (room)
    :param str scene_name:
        Name of scene
    """
    script_alias = f'{scene_name} - {group_name} (Scene)'
    script_name = f'hue_scene_{group_name}_{scene_name}'
    script_slug_name = script_name.replace(' ', '_').lower()
    script = {
        script_slug_name: {
            'alias': script_alias,
            'icon': 'mdi:lightbulb',
            'sequence': [
                {
                    'service': 'hue.hue_activate_scene',
                    'data': {
                        'group_name': group_name,
                        'scene_name': scene_name
                    }
                }
            ]
        }
    }
    with open(f'./scripts/{script_slug_name}.yaml', 'w') as stream:
        stream.write(yaml.dump(script, sort_keys=False))


if __name__ == '__main__':
    main()
