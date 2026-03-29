# MIT LED Control 💡
> Professional, Open Source Bluetooth Low Energy (BLE) controller for ELK-BLEDOM LED strips on Linux.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-brightgreen.svg)](https://www.python.org/)

[English](#english) | [Español](#español)

---

## English <a name="english"></a>

**MIT LED Control** is a desktop application designed for Fedora and other Linux distributions to manage RGB LED strips with an emphasis on stability and visual perfection.

### 🚀 Key Features
* **Zero-Residue Power Off:** Unlike other apps, this tool eliminates "ghost" light glow by forcing PWM to 0 and sending a pure black RGB burst.
* **On-Demand Authentication:** Respects your security. It only asks for `sudo` password when system Bluetooth management is strictly required.
* **Persistent Library:** Save your custom color profiles with names (e.g., "Movie Night", "Gaming").
* **Safe Reset:** Factory reset button is locked by default to prevent accidental data loss.
* **Responsive Interface:** Fully resizable UI with a smooth scroll area for large color libraries.

### 🛠 Technical Requirements
* **OS:** Linux (Tested on Fedora 40+)
* **Hardware:** Bluetooth 4.0+ adapter.
* **Dependencies:** `bleak`, `PyQt6`.

### 📦 Installation
```bash
# 1. Clone the repository
git clone [https://github.com/MitGamer890/MIT-Leds-Control.git](https://github.com/MitGamer890/MIT-Leds-Control.git)
cd MIT-Leds-Control

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
python3 mit_led_control.py
