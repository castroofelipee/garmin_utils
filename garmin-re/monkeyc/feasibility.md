# Connect IQ feasibility (FR55, VM 3.4.6)

- No Toybox API exposes sleep stages (REM/Light/Deep/Awake). ActivityMonitor and
  SensorHistory cover steps/HR/stress/body-battery only.
- CIQ apps are sandboxed: cannot read Garmin/Sleep/*.FIT or arbitrary device files.
- .PRG apps are signed/validated against the device StoreKey (RSA, see GarminDevice.xml).
  No supported native-call escape from MonkeyC bytecode to sleep symbols.
- Conclusion: a CIQ widget that reads LOCAL sleep stages cannot be built on FR55.
  Only cloud re-fetch is possible, which defeats the goal.
