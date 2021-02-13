#ifndef DISPLAY_H
#define DISPLAY_H

#include <Arduino.h>
#include <GFX.h>
#include <GxEPD2_3C.h>

// Display type GDEW075Z09 (7.5" 640x384)
// #define DISPLAY_TYPE GxEPD2_750c
// #include "ErrorImage_GDEW075Z09.h"
// #include "WifiImage_GDEW075Z09.h"

// Display type GDEW075Z08 (7.5" 800x480)
#define DISPLAY_TYPE GxEPD2_750c_Z08
#include "ErrorImage_GDEW075Z08.h"
#include "WifiImage_GDEW075Z08.h"

// A high-level wrapper around the e-paper display.
class Display {
 public:
  // Initializes the display for the next update.
  void Initialize();

  // Loads partial image data onto the display.
  void Load(const char* image_data, uint32_t size, uint32_t offset);

  // Shows the loaded image and sends the display to sleep.
  void Update();

  // Shows the error image.
  void ShowError();

  // Shows the Wifi setup image.
  void ShowWifiSetup();

  // Returns the width of the display in pixels.
  int16_t Width();

  // Returns the height of the display in pixels.
  int16_t Height();

 private:
  // Converts one pixel from 2-bit input encoding to 16-bit output encoding.
  uint16_t ConvertPixel(char input, char mask, int shift);

  // Initializes, loads, and shows a static image.
  void ShowStatic(const char* image, uint32_t size);

  // The entrypoint to the GxEPD2 tri-color e-paper display API.
  GxEPD2_3C<DISPLAY_TYPE, DISPLAY_TYPE::HEIGHT>* gx_epd_;
};

#endif  // DISPLAY_H
