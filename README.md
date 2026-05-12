# HearthWatch: Smart Stove Safety Sentinel

**Project Name:** HearthWatch  
**Developer:** Menden Cannistra  
**Date:** May 7, 2026  
**Platform:** Raspberry Pi Pico W (MicroPython)  

## Elevator Pitch
HearthWatch is a proactive kitchen safety system designed to prevent fires caused by human oversight. Unlike reactive smoke detectors, HearthWatch monitors **Localized Heat Differential ($\Delta T$)**, **Human Occupancy**, and **Time-Based Persistence** simultaneously. It triggers an audible alarm only when high-temperature conditions persist while the user is absent for a configurable timeout period, acting as an intelligent failsafe precursor system on the stovetop.

## Problem Statement
Existing safety solutions often fail to consider "Occupancy." Smart stoves monitor electrical function but lack intelligence regarding localized thermal buildup combined with human presence. Smoke alarms are reactive (triggering after damage). HearthWatch fills this gap by monitoring how long abnormal conditions persist without intervention before alerting the user, minimizing false positives through multi-sensor fusion.

## System Architecture & Hardware
The system is built on a **Raspberry Pi Pico W**, leveraging its GPIO/ADC I/O and MicroPython capabilities for embedded control.

### Hardware Components (SunFounder Kepler Kit)
| Component | Pin Assignment | Function |
| :--- | :--- | :--- |
| **DHT11 Sensor** | GPIO 14 | Ambient Temperature/Humidity Context |
| **NTC Thermistor** | ADC Pin 26 | Localized Hotspot Temperature (Voltage Divider) |
| **PIR Motion Sensor** | GPIO 15 | User Presence Detection (Occupancy Tracking) |
| **Active Buzzer** | GPIO 13 | Audible Warning Output |

## Detailed Wiring Guide & Implementation
This section details the physical implementation of the system, covering power rails, voltage dividers, and sensor connections. This ensures reproducibility for future iterations or team members.

### 1. Power & Ground Rails (The Foundation)
First, bridge your Pico W to the breadboard rails to provide stable power to all components:
*   **Pico Pin 40 (VBUS/5V)** → Breadboard Positive (+) Rail. *(Used for the PIR sensor)*
*   **Pico Pin 36 (3V3 OUT)** → Breadboard Second Positive (+) Rail. *(Used for DHT11 and Thermistor)*
*   **Pico Pin 38 (GND)** → Breadboard Negative (-) Rail.

### 2. The Thermistor Voltage Divider (The "Hotspot" Sensor)
This circuit converts resistance to a voltage the Pico can read using a fixed 10kΩ resistor:
*   **Node A (3.3V Source):** Connect one leg of the Thermistor to the 3.3V Rail.
*   **Node B (The Junction/Signal):** Connect the other leg of the Thermistor to a clean row on the breadboard (e.g., Row 20). In that same row, connect one leg of the 10kΩ Fixed Resistor and a jumper wire to Pico GP26.
*   **Node C (Ground):** Connect the remaining leg of the 10kΩ Fixed Resistor to the GND Rail.

### 3. PIR Motion Sensor (Occupancy)
The PIR has three pins, usually labeled on the board under the plastic dome:
*   **VCC / +:** Connect to the 5V (VBUS) Rail.
*   **OUT / Signal:** Connect to Pico GP15.
*   **GND / -:** Connect to the GND Rail.

### 4. DHT11 Sensor (Ambient Temp)
The DHT11 typically has three or four pins:
*   **VCC (+):** Connect to the 3.3V Rail.
*   **Data (S):** Connect to Pico GP14.
*   **GND (-):** Connect to the GND Rail.

### 5. Active Buzzer (The Alarm)
Identify the long and short pins on the buzzer:
*   **Long Pin (+):** Connect to Pico GP13.
*   **Short Pin (-):** Connect to the GND Rail.

## Circuit Diagrams & Schematics
Below is a custom hand-drawn schematic illustrating the complete hardware topology and signal flow for the system.

![Circuit Diagram](circuit_diagram.png)  

### Wiring Summary Table
| Component | Pin Type | Connection Point | Function |
| :--- | :--- | :--- | :--- |
| **Thermistor** | Leg 1 | 3.3V Rail (Pin 36) | Power input |
| **Thermistor** | Leg 2 | GP26 (Pin 31) | Signal Node |
| **10kΩ Resistor** | Leg 1 | GP26 (Pin 31) | Signal Node |
| **10kΩ Resistor** | Leg 2 | GND Rail (Pin 38) | Ground return |
| **PIR Sensor** | VCC | 5V Rail (Pin 40) | Power (5V) |
| **PIR Sensor** | OUT | GP15 (Pin 20) | Motion Signal |
| **PIR Sensor** | GND | GND Rail | Ground |
| **DHT11** | VCC | 3.3V Rail (Pin 36) | Power (3.3V) |
| **DHT11** | Data | GP14 (Pin 19) | Ambient Signal |
| **DHT11** | GND | GND Rail | Ground |
| **Active Buzzer** | (+) | GP13 (Pin 17) | Alarm Trigger |
| **Active Buzzer** | (-) | GND Rail | Ground |

## Software Development & Logic
The software is written in **MicroPython** and runs as a standalone script (`main.py`). It utilizes sensor fusion to ensure reliability.

### Core Logic Flow
1.  **Sensor Calibration:** The NTC thermistor uses the Steinhart-Hart equation with an empirical offset of `-8.87°C` determined through physical calibration against the DHT11 baseline. Your hardware may be different so it would be smart to adjust the offset accordingly. 
2.  **State Machine Logic:** The system triggers an alarm only when **all three** conditions are met simultaneously:
    *   $\Delta T \geq 4.0^\circ\text{C}$ (Hotspot vs. Ambient)
    *   User Absent (`PIR` sensor inactive for $>30$s)
    *   Duration Exceeded ($>30$ seconds configurable timeout)
3.  **Fail-Safe Error Handling:** If a sensor fails or drifts unexpectedly, the `try/except` block triggers continuous buzzer activity to prevent "false security" until the user inspects the device.

### Code Structure Highlights
```python
# Example: Safety Threshold Configuration
HEAT_THRESHOLD = 4.0      # ΔT required to trigger watch state (Configurable but this should be a nice value)
INACTIVITY_TIMEOUT = 30   # Seconds before warning (Configurable)

# Example: Sensor Fusion Logic
if delta_t >= HEAT_THRESHOLD and not is_occupied and current_unattended >= INACTIVITY_TIMEOUT:
    buzzer.value(1)  # Alert Triggered

### Demo & Presentation
Video Presentation: [Insert Your Video Link Here]
GitHub Repository: https://github.com/mendencan/HearthWatch

### Challenges Solved & Reflections

**1. Sensor Calibration Drift**
*   **Challenge:** The raw NTC thermistor readings varied significantly from the DHT11 baseline due to component tolerances. 
*   **Solution:** Implemented an empirical offset (`THERMISTOR_OFFSET = -8.87`) derived from physical testing, ensuring adequately accurate $\Delta T$ monitoring in a noisy kitchen environment.

**2. PIR Sensitivity & False Positives**
*   **Challenge:** The PIR sensor was initially too sensitive to ambient light or small movements (e.g., air movement).
*   **Solution:** Fine-tuned the sensitivity and implemented time-based persistence logic, ensuring the system only triggers when the user is truly absent for a sustained period.

**3. Error Handling & Reliability**
*   **Challenge:** A single sensor failure could lead to silent operation ("false security").
*   **Solution:** Added `try/except` blocks that trigger continuous buzzer activity on exception, forcing immediate physical inspection of the stovetop even if data is corrupted.

### Future Scalability & Roadmap
While the current prototype uses RAM-only storage, future iterations could include:
*   Non-volatile Logging: Use `machine.I2C` or SD card to log temperature history for trend analysis.
*   Networking Expansion: Utilize Pico W's Wi-Fi to host a local web dashboard (HTTP/REST API) for remote monitoring.
*   Industry Standard Sensors: Replace DHT11 with I2C sensors (e.g., SHT30) for higher precision and humidity compensation.

### Skills Applied in This Project
*   **Embedded Systems:** Raspberry Pi Pico W, MicroPython, GPIO/ADC I/O.
*   **Sensor Fusion & Calibration:** Combining DHT11 + NTC Thermistor + PIR data streams.
*   **Hardware Design:** Voltage divider circuits, breadboard prototyping, sensor tuning.
*   **Engineering Process:** Iterative Debugging, Hardware-Software combined design, real-time logic.

### License & Credits
*   **Kit:** SunFounder Kepler Ultimate Kit for Raspberry Pi Pico W 1.0
*   **AI Assistance:** Used AI tools to scaffold code structure and refine README documentation. 
*   **Author:** Menden Cannistra, CENG Freshman Lab Final Project.
