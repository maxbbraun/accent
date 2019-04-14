# Accent

Accent is a smart picture frame with a pop of color and no cables. Read more about it [on Medium](https://medium.com/@maxbraun/meet-accent-352cfa95813a).

[![Accent](accent.gif)](https://medium.com/@maxbraun/meet-accent-352cfa95813a)

## Server

The Accent server is built on [Google App Engine Python Standard Environment](https://cloud.google.com/appengine/docs/standard/python/).

To add user-specific data:
1. [Obtain a Google Maps API key](https://cloud.google.com/maps-platform/#get-started) and add it to [`user_data.py`](server/user_data.py#L5).
2. Add home and work addresses and a commute travel mode to [`user_data.py`](server/user_data.py#L8).
3. [Authenticate with the Google Calendar API](https://colab.research.google.com/drive/1mcgu_8cxxb-MMDKICr8oy9kFPSFPYlZ7#sandboxMode=true&scrollTo=ThqaE4cyA4R1) to create `g_calendar_secrets.json` and `g_calendar_credentials.json`, then save them to [`server`](server).
4. [Obtain a Dark Sky API key](https://darksky.net/dev) and add it to [`user_data.py`](server/user_data.py#L19).

To test and deploy the server:
1. [Install the Google Cloud SDK](https://cloud.google.com/sdk/docs/).
2. Run `cd server && virtualenv venv && . venv/bin/activate`.
3. Run `pip install -r requirements_bundled.txt -r requirements.txt`.
4. Run `pip install -t lib -r requirements.txt`.
5. Run the server locally with `dev_appserver.py app.yaml`.
6. Test the local server with:
   - [/next](http://localhost:8080/next) for the time in milliseconds until the next schedule entry.
   - [/epd](http://localhost:8080/epd) for the currently scheduled 2-bit image used by the e-paper display.
   - [/png](http://localhost:8080/png) for a PNG version of the currently scheduled image for easier debugging.
   - [/artwork](http://localhost:8080/artwork) to bypass the schedule and get the artwork image directly.
   - [/city](http://localhost:8080/city) to bypass the schedule and get the city image directly.
   - [/commute](http://localhost:8080/commute) to bypass the schedule and get the commute image directly.
   - [/calendar](http://localhost:8080/calendar) to bypass the schedule and get the calendar image directly.
7. Deploy the server with `gcloud app deploy`.

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
