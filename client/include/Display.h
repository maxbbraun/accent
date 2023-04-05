#ifndef DISPLAY_H
#define DISPLAY_H

#include <Arduino.h>
#include <GFX.h>
#include "ErrorImage.h"
#include "WifiImage.h"

// Display type GDEW075Z09 (7.5" 640x384 3-color)
#ifdef DISPLAY_GDEW075Z09
#include <GxEPD2_3C.h>
#define GFX_CLASS GxEPD2_3C
#define DISPLAY_TYPE GxEPD2_750c
#define PAGE_HEIGHT GxEPD2_750c::HEIGHT
#define VARIANT kVariant3Color
#endif

// Display type GDEW075Z08 (7.5" 800x480 3-color)
#ifdef DISPLAY_GDEW075Z08
#include <GxEPD2_3C.h>
#define GFX_CLASS GxEPD2_3C
#define DISPLAY_TYPE GxEPD2_750c_Z08
#define PAGE_HEIGHT GxEPD2_750c_Z08::HEIGHT
#define VARIANT kVariant3Color
#endif

// Display type GDEH075Z90 (7.5" 880x528 3-color)
#ifdef DISPLAY_GDEH075Z90
#include <GxEPD2_3C.h>
#define GFX_CLASS GxEPD2_3C
#define DISPLAY_TYPE GxEPD2_750c_Z90
#define PAGE_HEIGHT (GxEPD2_750c_Z90::HEIGHT / 2)
#define VARIANT kVariant3Color
#endif

// Display type GDEY1248Z51 (12.48" 1304x984 3-color)
#ifdef DISPLAY_GDEY1248Z51
#include <GxEPD2_3C.h>
#define GFX_CLASS GxEPD2_3C
#define DISPLAY_TYPE GxEPD2_1248c
#define PAGE_HEIGHT (GxEPD2_1248c::HEIGHT / 4)
#define VARIANT kVariant3Color
#endif

// Display type GDEY073D46 (7.3" 800x480 7-color)
#ifdef DISPLAY_GDEY073D46
#include <GxEPD2_7C.h>
#define GFX_CLASS GxEPD2_7C
#define DISPLAY_TYPE GxEPD2_730c_GDEY073D46
#define PAGE_HEIGHT (GxEPD2_730c_GDEY073D46::HEIGHT / 2)
#define VARIANT kVariant7Color
#endif

// A high-level wrapper around the e-paper display.
class Display {
 public:
  Display(uint32_t serial_speed) : serial_speed_(serial_speed) {}

  // Initializes the display connection and buffers.
  void Initialize();

  // Loads partial image data onto the display and updates after each page.
  void Load(const uint8_t* image_data, uint32_t size, uint32_t offset);

  // Frees display buffers and sends the display to sleep.
  void Finalize();

  // Shows the error image.
  void ShowError();

  // Shows the Wifi setup image.
  void ShowWifiSetup();

  // Returns the width of the display in pixels.
  int16_t Width();

  // Returns the height of the display in pixels.
  int16_t Height();

  // Returns the variant (number of colors) of the display.
  String Variant();

 private:
  // Converts one pixel from input encoding to display color encoding.
  uint16_t ConvertPixel(uint8_t input, uint8_t mask, uint8_t shift);

  // Initializes, loads, and finalizes a static image.
  void ShowStatic(const uint8_t* black_data, const uint8_t* red_data,
                  uint16_t width, uint16_t height, uint16_t background);

  // The entrypoint to the GxEPD2 tri-color e-paper display API.
  GFX_CLASS<DISPLAY_TYPE, PAGE_HEIGHT>* gx_epd_;

  // The baud rate for the serial connection. Used for GxEPD2 logging.
  uint32_t serial_speed_;
};

#endif  // DISPLAY_H
