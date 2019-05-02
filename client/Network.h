#ifndef NETWORK_H
#define NETWORK_H

#include <Arduino.h>
#include <HTTPClient.h>

// A high-level wrapper around Wifi connections and HTTP requests.
class Network {
 public:
  // Connects to a Wifi access point with the stored credentials.
  void connectWifi();

  // Opens a HTTP GET connection with the specified URL.
  bool httpGet(HTTPClient* http, String url);

 private:
  // Adds a basic access authentication header to the HTTP request.
  void addAuthHeader(HTTPClient* http);
};

#endif  // NETWORK_H
