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
