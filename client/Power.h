#ifndef POWER_H
#define POWER_H

#include <Arduino.h>

// A high-level wrapper around power management.
class Power {
 public:
  // Starts a deep sleep for a fixed time in milliseconds.
  void deepSleep(uint64_t delay_ms);

 private:
  // Sets all power domain configs to off.
  void applyConfigs();
};

#endif  // POWER_H
