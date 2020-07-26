#include "DisplayHD.h"

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

int16_t DisplayHD::Width() { return 880; }

int16_t DisplayHD::Height() { return 528; }

void DisplayHD::Initialize() {
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

  SendCommand(0x12); 		  //SWRESET
  WaitForIdle();        //waiting for the electronic paper IC to release the idle signal

  SendCommand(0x46);  // Auto Write RAM
  SendData(0xF7);
  WaitForIdle();        //waiting for the electronic paper IC to release the idle signal

  SendCommand(0x47);  // Auto Write RAM
  SendData(0xF7);
  WaitForIdle();        //waiting for the electronic paper IC to release the idle signal

  SendCommand(0x0C);  // Soft start setting
  SendData(0xAE);
  SendData(0xC7);
  SendData(0xC3);
  SendData(0xC0);
  SendData(0x40);   

  SendCommand(0x01);  // Set MUX as 527
  SendData(0xAF);
  SendData(0x02);
  SendData(0x01);

  SendCommand(0x11);  // Data entry mode (Y+, X-)
  SendData(0x01);

  SendCommand(0x44);
  SendData(0x00); // RAM x address start at 0
  SendData(0x00);
  SendData(0x6F); // RAM x address end at 36Fh -> 879
  SendData(0x03);
  // SendData(0x7F); // RAM x address end at 36Fh -> 639
  // SendData(0x02);
  SendCommand(0x45);
  SendData(0xAF); // RAM y address start at 20Fh;
  SendData(0x02);
  SendData(0x00); // RAM y address end at 00h;
  SendData(0x00);

  SendCommand(0x3C); // VBD
  SendData(0x01); // LUT1, for white

  SendCommand(0x18);
  SendData(0X80);
  SendCommand(0x22);
  SendData(0XB1);	//Load Temperature and waveform setting.
  SendCommand(0x20);
  WaitForIdle();        //waiting for the electronic paper IC to release the idle signal

  SendCommand(0x4E); 
  SendData(0x00);
  SendData(0x00);
  SendCommand(0x4F); 
  SendData(0xAF);
  SendData(0x02);
}

void DisplayHD::Load(const char* image_data, size_t length) {
  Serial.printf("Loading image data: %d bytes\n", length);
  
  SendCommand(0x24);     	//BLACK
  // Look at the image data one byte at a time, which is 4 input pixels.
  for (int i = 0; i < length; i+=2) {
    // Read all the black bits for 8 pixels from two image bytes 
    // image bytes are formatted as RBRBRBRB
    uint8_t value = ReadBlackData(image_data+i);
    SendData(value);
  }

  SendCommand(0x26);			//RED
  for (int i = 0; i < length; i+=2) {
    // Read all the red bits for 8 pixels
    uint8_t value = ReadRedData(image_data+i);
    SendData(value);
  }
}

uint8_t DisplayHD::ReadBlackData(const char * ptr) {
  return ((ptr[0] & 0x00000001)
      | ((ptr[0] & 0x00000040) >> 3)
      | ((ptr[0] & 0x00000010) >> 2)
      | ((ptr[0] & 0x00000004) >> 1) ) << 4
      | (ptr[1] & 0x00000001)
      | ((ptr[1] & 0x00000040) >> 3)
      | ((ptr[1] & 0x00000010) >> 2)
      | ((ptr[1] & 0x00000004) >> 1);
}

uint8_t DisplayHD::ReadRedData(const char * ptr) {
  return (((ptr[0] & 0x00000080) >> 4)
      | ((ptr[0] & 0x00000020) >> 3)
      | ((ptr[0] & 0x00000008) >> 2)
      | ((ptr[0] & 0x00000002) >> 1) ) << 4
      | ((ptr[1] & 0x00000080) >> 4)
      | ((ptr[1] & 0x00000020) >> 3)
      | ((ptr[1] & 0x00000008) >> 2)
      | ((ptr[1] & 0x00000002) >> 1);
}

void DisplayHD::Update() {
  // Refresh the display
  SendCommand(0x22);
  SendData(0xC7);
  SendCommand(0x20);
  delay(100);
  WaitForIdle(); 
  
  SendCommand(0x10);  	//deep sleep
  SendData(0x01);
}

void DisplayHD::ShowError() { ShowStatic(kErrorImage, sizeof(kErrorImage)); }

void DisplayHD::ShowWifiSetup() { ShowStatic(kWifiImage, sizeof(kWifiImage)); }

void DisplayHD::Reset() {
  digitalWrite(PIN_SPI_RST, LOW);
  delay(2);
  digitalWrite(PIN_SPI_RST, HIGH);
  delay(200);
}

void DisplayHD::SendCommand(uint8_t command) {
  digitalWrite(PIN_SPI_DC, LOW);
  SendSpi(command);
}

void DisplayHD::SendData(uint8_t data) {
  digitalWrite(PIN_SPI_DC, HIGH);
  SendSpi(data);
}

void DisplayHD::SendSpi(uint8_t data) {
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

void DisplayHD::WaitForIdle() {
  uint8_t busy;
  do {
      busy = digitalRead(PIN_SPI_BUSY);
  } while(busy);
  delay(200);
}

void DisplayHD::SetDrawRegion(uint16_t start_x, uint16_t start_y, uint16_t width, uint16_t height) {
  SendCommand(0x44);
  SendData(0x00); // RAM x address start
  SendData(0x00);
  SendData(width - 1); // RAM x address end
  SendData((width - 1) >> 8);
  SendCommand(0x45);
  SendData(height - 1); // RAM y address start 
  SendData((height - 1) >> 8);
  SendData(0x00); // RAM y address end at 00h;
  SendData(0x00);

  // Set drawing position
  SendCommand(0x4E); 
  SendData(start_x);
  SendData(start_x >> 8);
  SendCommand(0x4F); 
  SendData(687 - start_y);
  SendData((687 - start_y) >> 8);
}

void DisplayHD::ShowStatic(const char* image_data, unsigned long length) {
  Serial.println("Showing static image");

  Initialize();

  // Set drawing region to be size of static image (640x384) centered
  uint16_t x_diff = Width() - 640;
  uint16_t y_diff = Height() - 384;
  SetDrawRegion(x_diff/2, y_diff/2, 640, 384);
  
  const char* image_ptr = image_data;
  const char* image_end = image_ptr + length - 1 /* null terminator */;
  size_t chunk_length = static_cast<size_t>(image_end - image_ptr);
  Load(image_ptr, chunk_length);
  Update();
}
