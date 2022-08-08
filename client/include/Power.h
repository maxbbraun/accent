#ifndef POWER_H
#define POWER_H

#include <Arduino.h>

// A high-level wrapper around power management.
class Power {
 public:
  // Starts a deep sleep for a fixed time in milliseconds.
  void DeepSleep(uint64_t delay_ms);

  // Restarts immediately.
  void Restart();

 private:
  // Sets all power domain configs to off.
  void ApplyConfigs();
};

#endif  // POWER_H
