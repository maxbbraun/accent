#include "Display.h"

// The SPI pin definitions.
#define PIN_SPI_SCK 13
#define PIN_SPI_DIN 14
#define PIN_SPI_CS 15
#define PIN_SPI_BUSY 25
#define PIN_SPI_RST 26
#define PIN_SPI_DC 27

// The length in bytes per chunk when sending a static image.
const size_t kStaticImageChunkLength = 1024;

void Display::initialize() {
  Serial.println("Initializing display");

  // Initialize SPI.
  pinMode(PIN_SPI_BUSY, INPUT);
  pinMode(PIN_SPI_RST, OUTPUT);
  pinMode(PIN_SPI_DC, OUTPUT);
  pinMode(PIN_SPI_SCK, OUTPUT);
  pinMode(PIN_SPI_DIN, OUTPUT);
  pinMode(PIN_SPI_CS, OUTPUT);
  digitalWrite(PIN_SPI_CS, HIGH);
  digitalWrite(PIN_SPI_SCK, LOW);

  // Initialize the display.
  reset();
  sendCommandArgs(0x01, "\x37\x00");          // POWER_SETTING
  sendCommandArgs(0x00, "\xCF\x08");          // PANEL_SETTING
  sendCommandArgs(0x06, "\xC7\xCC\x28");      // BOOSTER_SOFT_START
  sendCommand(0x4);                           // POWER_ON
  waitForIdle();
  sendCommandArgs(0x30, "\x3C");              // PLL_CONTROL
  sendCommandArgs(0x41, "\x00");              // TEMPERATURE_CALIBRATION
  sendCommandArgs(0x50, "\x77");              // VCOM_AND_DATA_INTERVAL_SETTING
  sendCommandArgs(0x60, "\x22");              // TCON_SETTING
  sendCommandArgs(0x61, "\x02\x80\x01\x80");  // TCON_RESOLUTION
  sendCommandArgs(0x82, "\x1E");              // VCM_DC_SETTING
  sendCommandArgs(0xE5, "\x03");              // FLASH MODE
  sendCommand(0x10);                          // DATA_START_TRANSMISSION_1
  delay(2);
}

void Display::load(const char* image_data, size_t length) {
  Serial.printf("Loading image data: %d bytes\n", length);

  // Look at the image data one byte at a time, which is 4 input pixels.
  for (int i = 0; i < length; i++) {
    // 4 input pixels.
    const char p1 = convertPixel(image_data[i], 0xC0, 6);
    const char p2 = convertPixel(image_data[i], 0x30, 4);
    const char p3 = convertPixel(image_data[i], 0x0C, 2);
    const char p4 = convertPixel(image_data[i], 0x03, 0);

    // 2 output pixels.
    sendData((p1 << 4) | p2);
    sendData((p3 << 4) | p4);
  }
}

void Display::update() {
  // Refresh.
  Serial.println("Refreshing image");
  sendCommand(0x12);  // DISPLAY_REFRESH
  delay(100);
  waitForIdle();

  // Sleep.
  Serial.println("Suspending display");
  sendCommand(0x02);  // POWER_OFF
  waitForIdle();
  sendCommandArgs(0x07, "\xA5");  // DEEP_SLEEP
}

void Display::showStatic(const char* image_data, unsigned long length) {
  Serial.println("Showing static image");

  initialize();

  const char* image_ptr = image_data;
  const char* image_end = image_ptr + length - 1 /* null terminator */;
  do {
    size_t chunk_length = min(kStaticImageChunkLength,
                              static_cast<size_t>(image_end - image_ptr));
    load(image_ptr, chunk_length);
    image_ptr += chunk_length;
  } while (image_ptr < image_end);

  update();
}

void Display::reset() {
  digitalWrite(PIN_SPI_RST, LOW);
  delay(200);
  digitalWrite(PIN_SPI_RST, HIGH);
  delay(200);
}

void Display::sendCommandArgs(char command, const char* args...) {
  sendCommand(command);
  for (; *args != '\0'; ++args) {
    sendData(*args);
  }
}

void Display::sendCommand(char command) {
  digitalWrite(PIN_SPI_DC, LOW);
  sendSpi(command);
}

void Display::sendData(char data) {
  digitalWrite(PIN_SPI_DC, HIGH);
  sendSpi(data);
}

void Display::sendSpi(char data) {
  digitalWrite(PIN_SPI_CS, LOW);
  for (int i = 0; i < 8; ++i) {
    if ((data & 0x80) == 0) {
      digitalWrite(PIN_SPI_DIN, LOW);
    } else {
      digitalWrite(PIN_SPI_DIN, HIGH);
    }
    data <<= 1;
    digitalWrite(PIN_SPI_SCK, HIGH);
    digitalWrite(PIN_SPI_SCK, LOW);
  }
  digitalWrite(PIN_SPI_CS, HIGH);
}

void Display::waitForIdle() {
  while (digitalRead(PIN_SPI_BUSY) == LOW /* busy */) {
    delay(100);
  }
}

char Display::convertPixel(char input, char mask, int shift) {
  const char value = (input & mask) >> shift;
  switch (value) {
    case 0x0:
      // Black: 00 -> 0000
      return 0x0;
    case 0x1:
      // White: 01 -> 0011
      return 0x3;
    case 0x3:
      // Red: 11 -> 0100
      return 0x4;
    default:
      Serial.printf("Unknown pixel value: 0x%04X\n", value);
      return 0x0;
  }
}
