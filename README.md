# Accent

Accent is a smart picture frame that knows your routine, blends in like paper, and doesn't need any cables. Read more about it in [this article](https://medium.com/@maxbraun/this-is-accent-352cfa95813a).

[![Accent](accent-stars.jpg)](https://medium.com/@maxbraun/this-is-accent-352cfa95813a)

## Server

The Accent server is built on [Google App Engine Python Standard Environment](https://cloud.google.com/appengine/docs/standard/python/).

To add user-specific data:
1. [Obtain a Google Maps API key](https://cloud.google.com/maps-platform/#get-started) and add it to [`commute_data.py`](server/commute_data.py#L3).
2. Add home and work addresses and a commute travel mode to [`commute_data.py`](server/commute_data.py#L6).
3. [Authenticate with the Google Calendar API](https://goo.gl/k2LVAh) to create `g_calendar_secrets.json` and `g_calendar_credentials.json`, then save them to [`server`](server).

To test the server locally:
1. Run `cd server && virtualenv venv && . venv/bin/activate`.
2. Run `pip install -r requirements.txt -r requirements_bundled.txt`.
3. Run the server with `dev_appserver.py --log_level=debug app.yaml`.

To deploy the server:
1. Run `pip install -t lib -r requirements.txt`.
2. Run `gcloud app deploy`.

## Client

The Accent client uses the [Arduino toolchain](https://www.arduino.cc/en/Main/Software) for the [Waveshare ESP32 board](https://www.waveshare.com/wiki/E-Paper_ESP32_Driver_Board).

To push the client code to the ESP32:
1. Add a Wifi SSID and password to [`credentials.h`](client/credentials.h#L36).
2. Add the server URL to [`credentials.h`](client/credentials.h#L46).
3. Use the board information in [`client.ino`](client/client.ino#L9) to set up the environment.
4. Verify and upload the sketch.

## Frame

Files describing the Accent frame hardware include:
- A [Blender](https://www.blender.org/) project for simulating materials: [`frame.blend`](frame/frame.blend)
- A blueprint with basic dimensions: [`frame.pdf`](frame/frame.pdf)
- A [Shaper Origin](https://www.shapertools.com/) design: [`frame.svg`](frame/frame.svg)
- A [FreeCAD](https://www.freecadweb.org/) project: [`frame.FCStd`](frame/frame.FCStd)
- A G-code file for CNC milling: [`frame.gcode`](frame/frame.gcode)
- 3D models in STEP and STL formats: [`frame.step`](frame/frame.step) & [`frame.stl`](frame/frame.stl)

## License

Copyright 2019 Max Braun

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
