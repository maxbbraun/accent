#ifndef NETWORK_H
#define NETWORK_H

#include <Arduino.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include "Display.h"
#include "Power.h"

// A high-level wrapper around Wifi connections and HTTP requests.
class Network {
 public:
  Network() : display_(), power_(), wifi_setup_server_(nullptr) {}
  ~Network() {
    if (wifi_setup_server_ != nullptr) {
      delete wifi_setup_server_;
    }
  }

  // Attempts to connect to a Wifi access point with the stored credentials.
  bool ConnectWifi();

  // Opens a HTTP GET connection with the specified URL.
  bool HttpGet(HTTPClient* http, const String& url);

  // Opens a HTTP GET connection with the specified URL. The list of parameters
  // is expected to come as alternating keys and values.
  bool HttpGet(HTTPClient* http, const String& base_url,
               const std::vector<String>& parameters);

  // Deletes any saved Wifi SSID and password.
  void ResetWifi();

  // Opens an access point and starts a web server for Wifi setup.
  bool StartWifiSetupServer();

  // Handles client requests to the Wifi setup web server.
  bool HandleWifiSetupServer();

 private:
  // Serves an HTML form for Wifi setup.
  void ShowWifiForm();

  // Saves the Wifi setup form data.
  void SaveWifiForm();

  // Sends a 404 Not Found response.
  void SendNotFound();

  // Adds a basic access authentication header to the HTTP request.
  void AddAuthHeader(HTTPClient* http);

  // A display helper library instance.
  Display display_;

  // A power helper library instance.
  Power power_;

  // The server handling for Wifi setup.
  WebServer* wifi_setup_server_;
};

#endif  // NETWORK_H
