#ifndef DISPLAY_H
#define DISPLAY_H

#include <Arduino.h>

// A high-level wrapper around the e-paper display.
class Display {
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

 private:
  // Wakes up the display from sleep.
  void Reset();

  // Sends a command with arguments.
  void SendCommandArgs(char command, const char* args...);

  // Sends one byte as a command.
  void SendCommand(char command);

  // Sends one byte as data.
  void SendData(char data);

  // Sends one byte over SPI.
  void SendSpi(char data);

  // Waits until the display is ready.
  void WaitForIdle();

  // Converts one pixel from 2-bit input encoding to 4-bit output encoding.
  char ConvertPixel(char input, char mask, int shift);

  // Initializes, loads, and shows a static image.
  void ShowStatic(const char* image, unsigned long length);
};

#endif  // DISPLAY_H
