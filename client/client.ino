#include <Arduino.h>
#include "display.h"
#include "error_image.h"
#include "sleep.h"
#include "wifi.h"

// Display: https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_(B)
// Board: https://www.waveshare.com/wiki/E-Paper_ESP32_Driver_Board
// Board Manager URL: https://dl.espressif.com/dl/package_esp32_index.json
// Board: ESP32 Dev Module

// The baud rate for the serial connection.
const long kSerialSpeed = 115200;

// The base URL for server requests.
const String kServerBaseUrl = "https://accent.ink/";

// The size in bytes of the streaming HTTP response and image buffers.
const size_t kStreamBufferSize = 1024;

// The time in milliseconds to wait before restarting after an error.
uint64_t kRestartDelayMs = 60 * 60 * 1000;

void setup() {
  // Workaround for a bug where sometimes waking up from deep sleep fails.
  // https://www.hackster.io/nickthegreek82/esp32-deep-sleep-tutorial-4398a7
  delay(500);

  Serial.begin(kSerialSpeed);

  // Connect to the Wifi access point.
  connectWifi();

  // Show the latest image.
  initDisplay();
  if (downloadImage()) {
    updateDisplay();
  }

  // Go to sleep until the next refresh.
  scheduleSleep();
}

void loop() {
  // The setup() function only returns if there was an error.
  showStaticImage(kErrorImage, sizeof(kErrorImage));

  Serial.println("Restarting after error");
  deepSleep(kRestartDelayMs);
}

// Streams the image from the server and sends it to the display in chunks.
bool downloadImage() {
  Serial.println("Downloading image");
  HTTPClient http;

  // Request the current image from the server.
  if (!httpGet(&http, kServerBaseUrl + "epd")) {
    return false;
  }

  // Start reading from the stream.
  char buffer[kStreamBufferSize];
  WiFiClient* stream = http.getStreamPtr();
  unsigned long total_count = 0;
  do {
    if (!http.connected()) {
      Serial.println("Connection lost");
      http.end();
      return false;
    }

    Serial.printf("%d bytes available\n", stream->available());

    // Fill the buffer.
    size_t count = stream->readBytes(buffer, sizeof(buffer));
    total_count += count;
    Serial.printf("Read %d bytes (%lu total)\n", count, total_count);

    // Send the buffer to the display.
    loadImage(buffer, count);
  } while (stream->available() > 0);

  Serial.println("Download complete");
  http.end();
  return true;
}

// Sleeps for a time received from the server.
void scheduleSleep() {
  Serial.println("Scheduling sleep");
  HTTPClient http;

  // Request the next wake time from the server.
  if (!httpGet(&http, kServerBaseUrl + "next")) {
    return;
  }

  // Read the sleep time from the server.
  String delay_ms_str = http.getString();
  http.end();
  Serial.printf("Sleep server response: %s\n", delay_ms_str.c_str());
  uint64_t delay_ms = strtoull(delay_ms_str.c_str(), NULL, 10);
  deepSleep(delay_ms);
}
