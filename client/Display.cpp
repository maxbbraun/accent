#include "Display.h"

#include "ErrorImage.h"
#include "WifiImage.h"

// The SPI pin definitions.
#define PIN_SPI_SCK 13
#define PIN_SPI_DIN 14
#define PIN_SPI_CS 15
#define PIN_SPI_BUSY 25
#define PIN_SPI_RST 26
#define PIN_SPI_DC 27

// The length in bytes per chunk when sending a static image.
const size_t kStaticImageChunkLength = 1024;

int16_t Display::Width() { return 640; }

int16_t Display::Height() { return 384; }

void Display::Initialize() {
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
  Reset();
  SendCommandArgs(0x01, "\x37\x00");          // POWER_SETTING
  SendCommandArgs(0x00, "\xCF\x08");          // PANEL_SETTING
  SendCommandArgs(0x06, "\xC7\xCC\x28");      // BOOSTER_SOFT_START
  SendCommand(0x4);                           // POWER_ON
  WaitForIdle();
  SendCommandArgs(0x30, "\x3C");              // PLL_CONTROL
  SendCommandArgs(0x41, "\x00");              // TEMPERATURE_CALIBRATION
  SendCommandArgs(0x50, "\x77");              // VCOM_AND_DATA_INTERVAL_SETTING
  SendCommandArgs(0x60, "\x22");              // TCON_SETTING
  SendCommandArgs(0x61, "\x02\x80\x01\x80");  // TCON_RESOLUTION
  SendCommandArgs(0x82, "\x1E");              // VCM_DC_SETTING
  SendCommandArgs(0xE5, "\x03");              // FLASH MODE
  SendCommand(0x10);                          // DATA_START_TRANSMISSION_1
  delay(2);
}

void Display::Load(const char* image_data, size_t length) {
  Serial.printf("Loading image data: %d bytes\n", length);

  // Look at the image data one byte at a time, which is 4 input pixels.
  for (int i = 0; i < length; i++) {
    // 4 input pixels.
    const char p1 = ConvertPixel(image_data[i], 0xC0, 6);
    const char p2 = ConvertPixel(image_data[i], 0x30, 4);
    const char p3 = ConvertPixel(image_data[i], 0x0C, 2);
    const char p4 = ConvertPixel(image_data[i], 0x03, 0);

    // 2 output pixels.
    SendData((p1 << 4) | p2);
    SendData((p3 << 4) | p4);
  }
}

void Display::Update() {
  // Refresh.
  Serial.println("Refreshing image");
  SendCommand(0x12);  // DISPLAY_REFRESH
  delay(100);
  WaitForIdle();

  // Sleep.
  Serial.println("Suspending display");
  SendCommand(0x02);  // POWER_OFF
  WaitForIdle();
  SendCommandArgs(0x07, "\xA5");  // DEEP_SLEEP
}

void Display::ShowError() { ShowStatic(kErrorImage, sizeof(kErrorImage)); }

void Display::ShowWifiSetup() { ShowStatic(kWifiImage, sizeof(kWifiImage)); }

void Display::Reset() {
  digitalWrite(PIN_SPI_RST, LOW);
  delay(200);
  digitalWrite(PIN_SPI_RST, HIGH);
  delay(200);
}

void Display::SendCommandArgs(char command, const char* args...) {
  SendCommand(command);
  for (; *args != '\0'; ++args) {
    SendData(*args);
  }
}

void Display::SendCommand(char command) {
  digitalWrite(PIN_SPI_DC, LOW);
  SendSpi(command);
}

void Display::SendData(char data) {
  digitalWrite(PIN_SPI_DC, HIGH);
  SendSpi(data);
}

void Display::SendSpi(char data) {
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

void Display::WaitForIdle() {
  while (digitalRead(PIN_SPI_BUSY) == LOW /* busy */) {
    delay(100);
  }
}

char Display::ConvertPixel(char input, char mask, int shift) {
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

void Display::ShowStatic(const char* image_data, unsigned long length) {
  Serial.println("Showing static image");

  Initialize();

  const char* image_ptr = image_data;
  const char* image_end = image_ptr + length - 1 /* null terminator */;
  do {
    size_t chunk_length = min(kStaticImageChunkLength,
                              static_cast<size_t>(image_end - image_ptr));
    Load(image_ptr, chunk_length);
    image_ptr += chunk_length;
  } while (image_ptr < image_end);

  Update();
}
