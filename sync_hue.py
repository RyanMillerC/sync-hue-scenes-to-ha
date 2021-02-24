import json
import sys
from os import environ

from phue import Bridge

try:
    bridge = Bridge(environ['HUE_BRIDGE_HOST'], environ['HUE_BRIDGE_USERNAME'])
except:
    print('Set HUE_BRIDGE_HOST and HUE_BRIDGE_USERNAME environment variables!')
    sys.exit(1)

print(bridge.get_light())
