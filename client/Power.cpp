#include "Power.h"

// The power domains to turn off for deep sleep.
const esp_sleep_pd_domain_t kPowerDomains[] = {
    ESP_PD_DOMAIN_RTC_PERIPH,
    ESP_PD_DOMAIN_RTC_SLOW_MEM,
    ESP_PD_DOMAIN_RTC_FAST_MEM,
    ESP_PD_DOMAIN_XTAL};

void Power::deepSleep(uint64_t delay_ms) {
  uint64_t delay_us = 1000 * delay_ms;
  Serial.printf("Sleeping for %llu us\n", delay_us);
  applyConfigs();
  esp_deep_sleep(delay_us);
}

void Power::applyConfigs() {
  for (auto power_domain : kPowerDomains) {
    if (esp_sleep_pd_config(power_domain, ESP_PD_OPTION_OFF) != ESP_OK) {
      Serial.printf("Failed to apply power domain config: %d\n", power_domain);
    }
  }
}
