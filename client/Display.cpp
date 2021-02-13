#include "Display.h"

// Waveshare ESP32 SPI pin assignments.
const int8_t kSpiPinMiso = 12;
const int8_t kSpiPinSck = 13;
const int8_t kSpiPinMosi = 14;
const int8_t kSpiPinCs = 15;
const int8_t kSpiPinBusy = 25;
const int8_t kSpiPinRst = 26;
const int8_t kSpiPinDc = 27;

// The size in bytes per chunk when sending a static image.
const uint32_t kStaticImageChunkSize = 1024;

void Display::Initialize() {
  Serial.println("Initializing display");

  // Allocate display buffers.
  gx_epd_ = new GxEPD2_3C<DISPLAY_TYPE, DISPLAY_TYPE::HEIGHT>(
      DISPLAY_TYPE(kSpiPinCs, kSpiPinDc, kSpiPinRst, kSpiPinBusy));
  gx_epd_->init();

  // Remap the Waveshare ESP32's non-standard SPI pins.
  SPI.end();
  SPI.begin(kSpiPinSck, kSpiPinMiso, kSpiPinMosi, kSpiPinCs);
}

void Display::Load(const char* image_data, uint32_t size, uint32_t offset) {
  Serial.printf("Loading image data: %lu bytes\n", size);

  // Look at the image data one byte at a time, which is 4 input pixels.
  for (int i = 0; i < size; ++i) {
    // Read 4 input pixels.
    char input = image_data[i];
    uint16_t pixels[] = {
        ConvertPixel(input, 0xC0, 6),
        ConvertPixel(input, 0x30, 4),
        ConvertPixel(input, 0x0C, 2),
        ConvertPixel(input, 0x03, 0)
    };

    // Write 4 output pixels.
    for (int in = 0; in < 4; ++in) {
      uint16_t pixel = pixels[in];
      uint32_t out = 4 * (offset + i) + in;
      int16_t x = out % gx_epd_->width();
      int16_t y = out / gx_epd_->width();
      gx_epd_->drawPixel(x, y, pixel);
    }
  }
}

void Display::Update() {
  Serial.println("Updating display");
  gx_epd_->display(true /* no power off */);

  Serial.println("Suspending display");
  gx_epd_->hibernate();

  // Free display buffers.
  delete gx_epd_;
}

void Display::ShowError() { ShowStatic(kErrorImage, sizeof(kErrorImage)); }

void Display::ShowWifiSetup() { ShowStatic(kWifiImage, sizeof(kWifiImage)); }

int16_t Display::Width() { return gx_epd_->width(); }

int16_t Display::Height() { return gx_epd_->height(); }

uint16_t Display::ConvertPixel(char input, char mask, int shift) {
  const char value = (input & mask) >> shift;
  switch (value) {
    case 0x0:
      return GxEPD_BLACK;
    case 0x1:
      return GxEPD_WHITE;
    case 0x3:
      return GxEPD_RED;
    default:
      Serial.printf("Unknown pixel value: 0x%04X\n", value);
      return GxEPD_BLACK;
  }
}

void Display::ShowStatic(const char* image_data, uint32_t size) {
  Serial.println("Showing static image");

  Initialize();

  const char* image_ptr = image_data;
  const char* image_end = image_ptr + size - 1 /* null terminator */;
  do {
    uint32_t chunk_size = min(kStaticImageChunkSize,
                              static_cast<uint32_t>(image_end - image_ptr));
    Load(image_ptr, chunk_size, image_ptr - image_data);
    image_ptr += chunk_size;
  } while (image_ptr < image_end);

  Update();
}
