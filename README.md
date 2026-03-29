# MIT LED Control 💡
> Professional, Open Source Bluetooth Low Energy (BLE) controller for ELK-BLEDOM LED strips on Linux.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-brightgreen.svg)](https://www.python.org/)

[English](#english) | [Español](#español)

---

## English <a name="english"></a>

**MIT LED Control** is a high-performance desktop application built with Python and PyQt6. It provides a stable and elegant interface to manage RGB LED strips on Linux distributions like Fedora.

### 🚀 Key Features

* **Zero-Residue Power Off:** Eliminates "ghost" light glow by forcing PWM to 0 and sending a pure black RGB burst.
* **On-Demand Authentication:** Requests sudo permissions only when Bluetooth stack management is required (Scanning/Connecting).
* **Smart Library:** Save, name, and manage your favorite color profiles with an integrated "Quick Delete" system.
* **Responsive UI:** Fully resizable interface with a smooth scroll area for extensive color collections.
* **Safe Reset:** Factory reset button is locked by a security toggle to prevent accidental data loss.

### 🛠 Installation

1.  **Install System Dependencies (Fedora):**
    ```bash
    sudo dnf install python3-devel bluez-libs
    ```

2.  **Clone & Setup:**
    ```bash
    git clone [https://github.com/MitGamer890/MIT-Leds-Control.git](https://github.com/MitGamer890/MIT-Leds-Control.git)
    cd MIT-Leds-Control
    pip install -r requirements.txt
    ```

3.  **Run:**
    ```bash
    python3 mit_led_control.py
    ```

---

## Español <a name="español"></a>

**MIT LED Control** es una aplicación de escritorio de alto rendimiento construida con Python y PyQt6. Ofrece una interfaz estable y elegante para gestionar tiras LED RGB en distribuciones Linux como Fedora.

### 🚀 Características Principales

* **Apagado de Residuo Cero:** Elimina el "brillo fantasma" forzando el PWM a 0 y enviando una ráfaga RGB negra pura.
* **Autenticación bajo demanda:** Solicita permisos sudo solo cuando es estrictamente necesario gestionar el Bluetooth (Escaneo/Conexión).
* **Biblioteca Inteligente:** Guarda, nombra y gestiona tus perfiles de color favoritos con un sistema de borrado rápido integrado.
* **Interfaz Adaptable:** UI totalmente redimensionable con área de desplazamiento fluida para grandes colecciones de colores.
* **Reset Seguro:** El botón de restablecimiento de fábrica está bloqueado por un interruptor de seguridad para evitar pérdida de datos accidental.

### 🛠 Instalación

1.  **Instalar Dependencias del Sistema (Fedora):**
    ```bash
    sudo dnf install python3-devel bluez-libs
    ```

2.  **Clonar y Configurar:**
    ```bash
    git clone [https://github.com/MitGamer890/MIT-Leds-Control.git](https://github.com/MitGamer890/MIT-Leds-Control.git)
    cd MIT-Leds-Control
    pip install -r requirements.txt
    ```

3.  **Ejecutar:**
    ```bash
    python3 mit_led_control.py
    ```

---

## License / Licencia

Distributed under the MIT License. See `LICENSE` for more information.

**Author:** MitGamer890
