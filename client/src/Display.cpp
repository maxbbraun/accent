#include "Display.h"

// Waveshare ESP32 SPI pin assignments.
const int8_t kSpiPinMiso = 12;
const int8_t kSpiPinSck = 13;
const int8_t kSpiPinMosi = 14;
const int8_t kSpiPinCs = 15;
const int8_t kSpiPinBusy = 25;
const int8_t kSpiPinRst = 26;
const int8_t kSpiPinDc = 27;

// Display color variant identifiers for the server request.
const String kVariant7Color = "7color";
const String kVariant3Color = "bwr";

void Display::Initialize() {
  Serial.println("Initializing display");

  // Allocate display buffers.
  gx_epd_ = new GFX_CLASS<DISPLAY_TYPE, PAGE_HEIGHT>(
#ifdef DISPLAY_GDEY1248Z51
      // Configure the DESPI-C1248 connection board for this display type.
      GxEPD2_1248c(kSpiPinSck, kSpiPinMiso, kSpiPinMosi, /* CS M1 */ 23,
                   /* CS S1 */ 22, /* CS M2 */ 16, /* CS S2 */ 19,
                   /* DC 1 */ 25, /* DC 2 */ 17, /* RST 1 */ 33, /* RST 2 */ 5,
                   /* BUSY M1 */ 32, /* BUSY S1 */ 26, /* BUSY M2 */ 18,
                   /* BUSY S2 */ 4)
#else
      // Use the standard Waveshare configuration for all other display types.
      DISPLAY_TYPE(kSpiPinCs, kSpiPinDc, kSpiPinRst, kSpiPinBusy)
#endif
  );
  gx_epd_->init(serial_speed_);

  // Remap the Waveshare ESP32's non-standard SPI pins.
  SPI.end();
  SPI.begin(kSpiPinSck, kSpiPinMiso, kSpiPinMosi, kSpiPinCs);

  // Start paged drawing.
  gx_epd_->firstPage();
}

void Display::Load(const uint8_t* image_data, uint32_t size, uint32_t offset) {
  Serial.printf("Loading image data: %lu bytes\n", size);

  // The number of pixels per input byte depends on the display variant.
  const uint8_t pixels_per_byte = (Variant() == kVariant7Color ? 2 : 4);

  // Look at the image data one byte at a time.
  for (int i = 0; i < size; ++i) {
    // Convert the input byte to display pixels.
    uint8_t input = image_data[i];
    uint16_t pixels[pixels_per_byte];
    if (Variant() == kVariant7Color) {
      // Read 2 4-bit input pixels per byte.
      pixels[0] = ConvertPixel(input, 0xF0, 4);
      pixels[1] = ConvertPixel(input, 0x0F, 0);
    } else {  // Variant() == kVariant3Color
      // Read 4 2-bit input pixels per byte.
      pixels[0] = ConvertPixel(input, 0xC0, 6);
      pixels[1] = ConvertPixel(input, 0x30, 4);
      pixels[2] = ConvertPixel(input, 0x0C, 2);
      pixels[3] = ConvertPixel(input, 0x03, 0);
    }

    // Write the output pixels.
    for (int in = 0; in < pixels_per_byte; ++in) {
      uint16_t pixel = pixels[in];
      uint32_t out = pixels_per_byte * (offset + i) + in;
      int16_t x = out % gx_epd_->width();
      int16_t y = out / gx_epd_->width();
      gx_epd_->drawPixel(x, y, pixel);

      // Trigger a display update after the last pixel of each page.
      if ((y + 1) % gx_epd_->pageHeight() == 0 && x == gx_epd_->width() - 1) {
        Serial.println("Updating display");
        gx_epd_->nextPage();
      }
    }
  }
}

void Display::Finalize() {
  Serial.println("Suspending display");
  gx_epd_->hibernate();

  // Free display buffers.
  delete gx_epd_;
}

void Display::ShowError() {
  ShowStatic(kErrorImageBlack, kErrorImageRed, kErrorWidth, kErrorHeight,
             kErrorBackground);
}

void Display::ShowWifiSetup() {
  ShowStatic(kWifiImageBlack, kWifiImageRed, kWifiWidth, kWifiHeight,
             kWifiBackground);
}

int16_t Display::Width() { return gx_epd_->width(); }

int16_t Display::Height() { return gx_epd_->height(); }

String Display::Variant() { return VARIANT; }

uint16_t Display::ConvertPixel(uint8_t input, uint8_t mask, uint8_t shift) {
  // Isolate the relevant bits from the input.
  uint8_t value = (input & mask) >> shift;

  // Convert the input value to a display color.
  if (Variant() == kVariant7Color) {
    switch (value) {
      case 0x0:
        return GxEPD_BLACK;
      case 0x1:
        return GxEPD_WHITE;
      case 0x2:
        return GxEPD_GREEN;
      case 0x3:
        return GxEPD_BLUE;
      case 0x4:
        return GxEPD_RED;
      case 0x5:
        return GxEPD_YELLOW;
      case 0x6:
        return GxEPD_ORANGE;
      default:
        Serial.printf("Unknown 7-color value: 0x%02X\n", value);
        return GxEPD_BLACK;
    }
  } else {  // Variant() == kVariant3Color
    switch (value) {
      case 0x0:
        return GxEPD_BLACK;
      case 0x1:
        return GxEPD_WHITE;
      case 0x3:
        return GxEPD_RED;
      default:
        Serial.printf("Unknown 3-color value: 0x%02X\n", value);
        return GxEPD_BLACK;
    }
  }
}

void Display::ShowStatic(const uint8_t* black_data, const uint8_t* red_data,
                         uint16_t width, uint16_t height, uint16_t background) {
  Serial.println("Showing static image");

  Initialize();

  // Calculate the offset to center the static image in the display.
  int16_t x = (gx_epd_->width() - width) / 2;
  int16_t y = (gx_epd_->height() - height) / 2;

  do {
    // Fill in the background first.
    gx_epd_->fillScreen(background);

    // Draw the static image one color at a time.
    gx_epd_->fillRect(x, y, width, height, GxEPD_WHITE);
    gx_epd_->drawBitmap(x, y, black_data, width, height, GxEPD_BLACK);
    gx_epd_->drawBitmap(x, y, red_data, width, height, GxEPD_RED);
  } while (gx_epd_->nextPage());

  Finalize();
}
