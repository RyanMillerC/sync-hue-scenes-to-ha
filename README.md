# Sync Philips Hue Scenes to Home Assistant

This script will sync scenes from Philips Hue into Home Assistant (HA).

Because of how Hue scenes are designed, they can only be set by HA and
not read. This means they can not be imported or used like HA scenes.

Instead, this script will add an HA script entity for each Hue scene. The
scripts will call a given Hue scene when activated in HA.

This script requires that your Hue Bridge information be set in
environment variables as: (replace contents in '<>' with your info)

```bash
export HUE_BRIDGE_HOST='<IP of Hue bridge>'
export HUE_BRIDGE_USERNAME='<Username/token for Hue bridge auth>
```
