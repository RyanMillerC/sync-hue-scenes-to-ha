"""
# Sync Philips Hue Scenes to Home Assistant

This script will sync scenes from Philips Hue into Home Assistant (HA).

Because of how Hue scenes are designed, they can only be set by HA and
not read. This means they can not be imported or used like HA scenes.

Instead, this script will add an HA script entity for each Hue scene. The
scripts will call a given Hue scene when activated in HA.

## Requirements

* 1 or more Philips Hue bridges configured in Home Assistant through the Hue integration
* A `./scripts` directory in your Home Assistant config directory
* *configuration.yaml* must include the line: `script: !include_dir_merge_named scripts/`

## Set Up

Set up this script outside of your Home Assistant config directory.

```
git clone https://github.com/RyanMillerC/sync-hue-scenes-to-ha.git
cd sync-hue-scenes-to-ha
pip install --user -r requirements.txt
```

## Running

To run:

```bash
python sync_hue.py <path-to-home-assistant-config>
```
"""


import glob
import json
import os
import sys
import yaml

from phue import Bridge


# These scene names will be skipped. Add additional scene names to
# skip if needed.
DEFAULT_SCENE_NAMES = [
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


try:
    HOME_ASSISTANT_CONFIG_DIR = sys.argv[1]
    os.chdir(HOME_ASSISTANT_CONFIG_DIR)
except IndexError:
    print('Usage: python sync_hue.py <path-to-home-assistant-config>')
    sys.exit(1)


def main():
    """Execute rest of script."""
    remove_existing_scripts()
    bridges = get_hue_bridges()
    print(f'Found {len(bridges)} bridge(s)!')
    for bridge in bridges:
        print(f'Processing bridge "{bridge.name}" ({bridge.ip})...')
        rooms = get_rooms(bridge)
        scenes = get_scenes(bridge)
        mapped_scenes = map_scenes_to_rooms(scenes, rooms)
        for group_name, scene_name in mapped_scenes:
            create_yaml(group_name, scene_name)
        print(f'Completed bridge "{bridge.name} ({bridge.ip})"!')


def get_hue_bridges():
    """Get hue bridge IPs and usernames from HA file."""
    with open(f'./.storage/core.config_entries', 'r') as stream:
        config_entries = json.load(stream)
    bridge_info = [
        entry['data'] for entry in config_entries['data']['entries']
        if entry['domain'] == 'hue'
    ]
    bridges = [
        Bridge(info['host'], info['username']) for info in bridge_info
    ]
    return bridges


def remove_existing_scripts():
    """Remove existing HA scripts from previous run."""
    print('Removing previously generated hue_scene YAML scripts...')
    existing_scripts = glob.glob('./scripts/hue_scene_*.yaml')
    for script in existing_scripts:
        os.remove(script)


def get_rooms(bridge):
    """Get groups of type 'Room' from Hue API.

    :param phue.Bridge bridge:
        Hue bridge connection

    :returns: group_id, name, and lights of each room
    :rtype: dict
    """
    rooms = {}
    api_groups = bridge.get_group()
    for group_id, group_attributes in api_groups.items():
        if group_attributes['type'] == 'Room':
            rooms[group_id] = group_attributes
    return rooms


def get_scenes(bridge):
    """Get scenes from the Hue API. Will ignore all default Hue scenes.

    :param phue.Bridge bridge:
        Hue bridge connection

    :returns:
    :rtype: list
    """
    scenes = {}
    api_scenes = bridge.get_scene()
    for scene_id, scene_attributes in api_scenes.items():
        scene_name = scene_attributes['name']
        if scene_name in DEFAULT_SCENE_NAMES:
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
    script_file_path = f'./scripts/{script_slug_name}.yaml'
    print(f'Writing {script_file_path}...')
    with open(script_file_path, 'w') as stream:
        stream.write(yaml.dump(script, sort_keys=False))


if __name__ == '__main__':
    main()
