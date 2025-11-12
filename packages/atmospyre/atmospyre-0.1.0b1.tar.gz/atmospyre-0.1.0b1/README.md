# AtmosPyre

Python interface for Modbus-based environmental sensors.

**📖 [Full documentation](https://pages.iws.uni-stuttgart.de/measurements/atmospyre/)**

## Why AtmosPyre?

Write sensor drivers in ~100 lines of Python instead of buying expensive vendor software. AtmosPyre provides a consistent API for adding new sensors.

- 💰 No proprietary software licenses needed
- 🔧 Add new sensors quickly
- 🎯 Single API for all sensors
- 📝 Clear documentation and examples

## Installation

```bash
pip install atmospyre
```

Development mode:
```bash
git clone https://git.iws.uni-stuttgart.de/measurements/atmospyre.git
cd atmospyre
pip install -e ".[dev]"
```

**Requirements:** Python 3.10+, `minimalmodbus`, `multipledispatch`, `schedule`

## Example: Multi-Sensor Data Logging

This example demonstrates setting up multiple sensors on the same serial port and logging their data at different intervals:

**Hardware Setup:**
- GMP252 CO₂ sensor at address 121 (19200 baud, 2 stop bits)
- AlphaTRACER radon sensor at address 122 (19200 baud, 1 stop bit)
- Both connected to `/dev/ttyACM0`

The sensors automatically share the port without conflicts.

```python
import time
from atmospyre.sensors.implementations.co2 import gmp252
from atmospyre.sensors.implementations.radon import alphatracer
from atmospyre.sensors import Stopbits
from atmospyre.loggers import SensorLogger
from atmospyre.loggers.strategies.writers import CSVWriter
from atmospyre.loggers.strategies.savers import JSONMetadataSaver
from atmospyre.scheduler.logger_scheduler import LoggerScheduler
from atmospyre.scheduler.schedule.schedule_backend import ScheduleTag

def main():
    # CO2 Sensor - Vaisala GMP252
    co2_sensor = gmp252.GMP252(
        port='/dev/ttyACM0',
        slave_address=121
    )

    # Radon Sensor - RadonTech AlphaTRACER
    radon_sensor = alphatracer.AlphaTRACER(
        port='/dev/ttyACM0',
        slave_address=122,
        baudrate=19200,
        stopbits=Stopbits.ONE
    )

    # CO2 Logger - logs every 10 seconds
    co2_logger = SensorLogger(
        sensor=co2_sensor,
        tags=[gmp252.CO2, gmp252.MEASURED_TEMPERATURE],
        interval_seconds=10,
        output_path="./CO2Probe",
        writer=CSVWriter(),
        metadata_saver=JSONMetadataSaver()
    )

    # Radon Logger - logs every 10 minutes
    radon_logger = SensorLogger(
        sensor=radon_sensor,
        tags=[alphatracer.RADON_LIVE],
        interval_seconds=600,
        output_path="./RadonProbe",
        writer=CSVWriter(),
        metadata_saver=JSONMetadataSaver()
    )

    # Scheduler Setup
    scheduler = LoggerScheduler(
        scheduler_dispatch_tag=ScheduleTag(),
        log_path="./scheduler_logs"
    )

    scheduler.add_logger(logger=co2_logger)
    scheduler.add_logger(logger=radon_logger)

    # Run
    print("Starting multi-sensor data logging...")
    print(f"  - CO2 sensor: logging every 10 seconds to ./CO2Probe")
    print(f"  - Radon sensor: logging every 600 seconds to ./RadonProbe")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            scheduler.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping data logging...")

if __name__ == "__main__":
    main()
```

## Supported Sensors

- **Vaisala GMP252** — CO₂ and temperature
- **RadonTech AlphaTRACER** — Radon concentration

## Quick Links

- [Quick Start Guide](https://pages.iws.uni-stuttgart.de/measurements/atmospyre/getting_started/)
- [Adding a New Sensor](https://pages.iws.uni-stuttgart.de/measurements/atmospyre/dev/custom_sensor/)
- [API Reference](https://pages.iws.uni-stuttgart.de/measurements/atmospyre/api/)
- [PyPI Package](https://pypi.org/project/atmospyre/)