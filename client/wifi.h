#ifndef wifi_h
#define wifi_h

#include <HTTPClient.h>
#include <WiFi.h>
#include <base64.h>

// The trusted root certificate for HTTPS connections.
// https://valid.r1.roots.globalsign.com
// Valid until: 28 January 2028
const char* kRootCertificate =
    "-----BEGIN CERTIFICATE-----\n"
    "MIIDdTCCAl2gAwIBAgILBAAAAAABFUtaw5QwDQYJKoZIhvcNAQEFBQAwVzELMAkG\n"
    "A1UEBhMCQkUxGTAXBgNVBAoTEEdsb2JhbFNpZ24gbnYtc2ExEDAOBgNVBAsTB1Jv\n"
    "b3QgQ0ExGzAZBgNVBAMTEkdsb2JhbFNpZ24gUm9vdCBDQTAeFw05ODA5MDExMjAw\n"
    "MDBaFw0yODAxMjgxMjAwMDBaMFcxCzAJBgNVBAYTAkJFMRkwFwYDVQQKExBHbG9i\n"
    "YWxTaWduIG52LXNhMRAwDgYDVQQLEwdSb290IENBMRswGQYDVQQDExJHbG9iYWxT\n"
    "aWduIFJvb3QgQ0EwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDaDuaZ\n"
    "jc6j40+Kfvvxi4Mla+pIH/EqsLmVEQS98GPR4mdmzxzdzxtIK+6NiY6arymAZavp\n"
    "xy0Sy6scTHAHoT0KMM0VjU/43dSMUBUc71DuxC73/OlS8pF94G3VNTCOXkNz8kHp\n"
    "1Wrjsok6Vjk4bwY8iGlbKk3Fp1S4bInMm/k8yuX9ifUSPJJ4ltbcdG6TRGHRjcdG\n"
    "snUOhugZitVtbNV4FpWi6cgKOOvyJBNPc1STE4U6G7weNLWLBYy5d4ux2x8gkasJ\n"
    "U26Qzns3dLlwR5EiUWMWea6xrkEmCMgZK9FGqkjWZCrXgzT/LCrBbBlDSgeF59N8\n"
    "9iFo7+ryUp9/k5DPAgMBAAGjQjBAMA4GA1UdDwEB/wQEAwIBBjAPBgNVHRMBAf8E\n"
    "BTADAQH/MB0GA1UdDgQWBBRge2YaRQ2XyolQL30EzTSo//z9SzANBgkqhkiG9w0B\n"
    "AQUFAAOCAQEA1nPnfE920I2/7LqivjTFKDK1fPxsnCwrvQmeU79rXqoRSLblCKOz\n"
    "yj1hTdNGCbM+w6DjY1Ub8rrvrTnhQ7k4o+YviiY776BQVvnGCv04zcQLcFGUl5gE\n"
    "38NflNUVyRRBnMRddWQVDf9VMOyGj/8N7yy5Y0b2qvzfvGn9LhJIZJrglfCm7ymP\n"
    "AbEVtQwdpf5pLGkkeB6zpxxxYu7KyJesF12KwvhHhm4qxFYxldBniYUr+WymXUad\n"
    "DKqC5JlR3XC321Y9YeRq4VzW9v493kHMB65jUr9TU/Qr6cf9tveCX4XSQRjbgbME\n"
    "HMUfpIBvFSDJ3gyICh3WZlXi/EjJKSZp4A==\n"
    "-----END CERTIFICATE-----\n";

// The SSID of the Wifi access point to connect to.
const char* kWifiSsid = "SSID";

// The password of the Wifi access point to connect to.
const char* kWifiPassword = "PASSWORD";

// The time in milliseconds before timing out when reading HTTP data.
const uint16_t kReadTimeoutMs = 30 * 1000;

// Connects to the Wifi access point.
void connectWifi() {
  if (WiFi.isConnected()) {
    Serial.println("Already connected");
    return;
  }

  // Start connecting with SSID and password.
  Serial.printf("Connecting to \"%s\" .", kWifiSsid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(kWifiSsid, kWifiPassword);

  // Wait until connected.
  while (!WiFi.isConnected()) {
    delay(500);
    Serial.print(".");
  }
  Serial.printf("\nConnected to %s as %s\n", WiFi.SSID().c_str(),
                WiFi.localIP().toString().c_str());
}

// Adds a basic access authentication header to the HTTP request.
void addAuthHeader(HTTPClient* http) {
  // Use the Wifi MAC address as the unique client ID.
  String client_id = WiFi.macAddress();
  client_id.replace(":", "");  // Disallowed character

  // Add the header with the Base64-encoded authorization (no username).
  String authorization = base64::encode(":" + client_id);
  http->addHeader("Authorization", "Basic " + authorization);
}

// Opens a HTTP GET connection with the specified URL.
bool httpGet(HTTPClient* http, String url) {
  Serial.printf("Requesting URL: %s\n", url.c_str());

  if (!http->begin(url, kRootCertificate)) {
    Serial.printf("Failed to connect to server: %s\n", url.c_str());
    return false;
  }

  // Apply the read timeout after connecting.
  http->setTimeout(kReadTimeoutMs);

  // Authenticate the request.
  addAuthHeader(http);

  int status = http->GET();
  if (status <= 0) {
    Serial.printf("Request failed: %s\n", http->errorToString(status).c_str());
    http->end();
    return false;
  }

  Serial.printf("Status code: %d\n", status);
  if (status != HTTP_CODE_OK) {
    http->end();
    return false;
  }

  return true;
}

#endif  // wifi_h
