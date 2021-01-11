#ifndef DISPLAYHD_H
#define DISPLAYHD_H

#include <Arduino.h>

// A high-level wrapper around the e-paper display.
// This class supports the Waveshare 7.5 HD e-ink display
// https://www.waveshare.com/wiki/7.5inch_HD_e-Paper_HAT
class DisplayHD {
 public:
  // Initializes the display for the next update.
  void Initialize();

  // Loads partial image data onto the display.
  void Load(const char* image_data, size_t length);

  // Shows the loaded image and sends the display to sleep.
  void Update();

  // Shows the error image.
  void ShowError();

  // Shows the Wifi setup image.
  void ShowWifiSetup();

  // Return width of display in pixels
  int16_t Width();
  
  // Return height of display in pixels
  int16_t Height();

 private:
  // Wakes up the display from sleep.
  void Reset();

  // Sends one byte as a command.
  void SendCommand(uint8_t command);

  // Sends one byte as data.
  void SendData(uint8_t data);

  // Sends one byte over SPI.
  void SendSpi(uint8_t data);

  // Waits until the display is ready.
  void WaitForIdle();

  // Initializes, loads, and shows a static image.
  void ShowStatic(const char* image, unsigned long length);

  // Read the black data from two input pixels (8 output pixels/bits)
  uint8_t ReadBlackData(const char * ptr);
  
  // Read the red data from two input pixels (8 output pixels/bits)
  uint8_t ReadRedData(const char * ptr);

  // Set drawing region in order to render lower resolution images
  void SetDrawRegion(uint16_t start_x, uint16_t start_y, uint16_t width, uint16_t height);

};

#endif  // DISPLAYHD_H
