#ifndef DISPLAY_H
#define DISPLAY_H

#include <Arduino.h>

// A high-level wrapper around the e-paper display.
class Display {
 public:
  // Initializes the display for the next update.
  void initialize();

  // Loads partial image data onto the display.
  void load(const char* image_data, size_t length);

  // Shows the loaded image and sends the display to sleep.
  void update();

  // Initializes, loads, and shows a static image.
  void showStatic(const char* image, unsigned long length);

 private:
  // Wakes up the display from sleep.
  void reset();

  // Sends a command with arguments.
  void sendCommandArgs(char command, const char* args...);

  // Sends one byte as a command.
  void sendCommand(char command);

  // Sends one byte as data.
  void sendData(char data);

  // Sends one byte over SPI.
  void sendSpi(char data);

  // Waits until the display is ready.
  void waitForIdle();

  // Converts one pixel from 2-bit input encoding to 4-bit output encoding.
  char convertPixel(char input, char mask, int shift);
};

#endif  // DISPLAY_H
