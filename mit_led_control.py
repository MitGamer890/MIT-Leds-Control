import sys
import asyncio
import threading
import subprocess
import json
import os
from bleak import BleakClient
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFrame,
                             QColorDialog, QSlider, QListWidget, QStatusBar,
                             QGridLayout, QInputDialog, QLineEdit, QCheckBox, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QObject

# --- IDENTIDAD MIT ---
APP_NAME = "MIT LED Control"
WRITE_UUID = "0000fff3-0000-1000-8000-00805f9b34fb"
CONFIG_FILE = os.path.expanduser("~/.mit_led_control_config.json")

class BleManager(QObject):
    status_msg = pyqtSignal(str)
    connection_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.client = None
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _connect_task(self, mac, pwd):
        self.status_msg.emit("Sincronizando bus...")
        subprocess.run(f"echo '{pwd}' | sudo -S bluetoothctl remove {mac}", shell=True, capture_output=True)
        self.client = BleakClient(mac, timeout=15.0)
        try:
            await self.client.connect()
            if self.client.is_connected:
                self.connection_changed.emit(True)
                self.status_msg.emit("✓ Dispositivo Vinculado")
        except Exception as e:
            self.status_msg.emit(f"Error: {str(e)}")
            self.connection_changed.emit(False)

    async def _disconnect_task(self):
        if self.client and self.client.is_connected:
            await self.client.disconnect()
        self.loop.stop()

    def connect(self, mac, pwd): asyncio.run_coroutine_threadsafe(self._connect_task(mac, pwd), self.loop)

    def disconnect_and_exit(self):
        asyncio.run_coroutine_threadsafe(self._disconnect_task(), self.loop)

    def send_burst(self, cmds):
        if self.client and self.client.is_connected:
            for c in cmds:
                asyncio.run_coroutine_threadsafe(
                    self.client.write_gatt_char(WRITE_UUID, bytearray.fromhex(c), False), self.loop
                )

class MITLedControl(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sudo_password = ""
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(500, 850)

        self.ble = BleManager()
        self.ble.status_msg.connect(self.update_status)
        self.ble.connection_changed.connect(self.on_connection_change)

        self.custom_colors = self.load_settings()
        self.last_rgb = (208, 240, 255)

        self.init_ui()

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f: return json.load(f)
            except: pass
        return {"ff0000": "Rojo", "00ff00": "Verde", "0000ff": "Azul", "ffff00": "Amarillo", "d0f0ff": "Hielo"}

    def save_settings(self):
        with open(CONFIG_FILE, 'w') as f: json.dump(self.custom_colors, f)

    def ask_pwd_if_needed(self):
        """Pide la contraseña solo cuando se va a realizar una acción que requiere sudo."""
        if not self.sudo_password:
            text, ok = QInputDialog.getText(self, "Autenticación del Sistema",
                "Introduce tu contraseña de usuario (sudo).\n\n"
                "Esta contraseña es necesaria para que la aplicación pueda gestionar\n"
                "el adaptador Bluetooth de Linux y eliminar rastros de conexiones previas.",
                QLineEdit.EchoMode.Password)
            if ok and text:
                self.sudo_password = text
                return True
            return False
        return True

    def init_ui(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #050505; }
            QLabel { color: #555; font-family: 'Segoe UI'; font-size: 10px; font-weight: 800; letter-spacing: 2px; }
            QListWidget { background-color: #0a0a0a; color: #2196f3; border: 1px solid #1a1a1a; border-radius: 8px; }
            QPushButton { background-color: #111; color: #eee; border-radius: 6px; padding: 12px; border: 1px solid #222; font-weight: bold; font-size: 11px; }
            QPushButton:hover { background-color: #1a1a1a; border-color: #333; }
            QPushButton#btnOn { border-bottom: 3px solid #2e7d32; color: #4caf50; }
            QPushButton#btnOff { border-bottom: 3px solid #c62828; color: #ef5350; }
            QPushButton#btnReset { background-color: #200; color: #f66; border-color: #400; }
            QPushButton#btnReset:disabled { background-color: #050505; color: #333; border-color: #111; }
            QPushButton#btnExit { background-color: #151515; color: #888; border: 1px solid #222; margin-top: 10px; }
            QPushButton#btnExit:hover { background-color: #200; color: #fff; border-color: #f00; }
            QFrame#card { background-color: #080808; border-radius: 20px; border: 1px solid #121212; }
            QScrollArea { border: none; background-color: transparent; }
            QSlider::groove:horizontal { height: 2px; background: #222; }
            QSlider::handle:horizontal { background: #fff; width: 14px; height: 14px; margin: -6px 0; border-radius: 7px; }
        """)

        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(30, 40, 30, 40)
        layout.setSpacing(20)

        # HEADER
        top_bar = QHBoxLayout()
        header_title = QLabel("MIT LED CONTROL")
        header_title.setStyleSheet("color: #2196f3; font-size: 22px; font-weight: 900; letter-spacing: 8px;")
        self.check_unlock = QCheckBox("Unlock Reset")
        self.check_unlock.setStyleSheet("color: #333; font-size: 9px;")
        self.btn_reset = QPushButton("RESET")
        self.btn_reset.setObjectName("btnReset")
        self.btn_reset.setEnabled(False)
        self.check_unlock.toggled.connect(self.btn_reset.setEnabled)
        self.btn_reset.clicked.connect(self.factory_reset)
        top_bar.addWidget(header_title); top_bar.addStretch(); top_bar.addWidget(self.check_unlock); top_bar.addWidget(self.btn_reset)
        layout.addLayout(top_bar)

        # DISPOSITIVOS
        layout.addWidget(QLabel("NODOS BLUETOOTH"))
        self.list_ui = QListWidget(); self.list_ui.setMinimumHeight(100); layout.addWidget(self.list_ui)
        scan_box = QHBoxLayout()
        btn_scan = QPushButton("SCAN"); btn_scan.clicked.connect(self.start_scan)
        btn_pair = QPushButton("CONNECT"); btn_pair.clicked.connect(self.init_connection)
        scan_box.addWidget(btn_scan); scan_box.addWidget(btn_pair); layout.addLayout(scan_box)

        # PANEL CONTROL
        self.panel = QFrame(); self.panel.setObjectName("card"); self.panel.setEnabled(False)
        p_layout = QVBoxLayout(self.panel); p_layout.setContentsMargins(25, 25, 25, 25)

        p_layout.addWidget(QLabel("POWER"))
        power_box = QHBoxLayout()
        btn_on = QPushButton("ON"); btn_on.setObjectName("btnOn"); btn_on.clicked.connect(self.action_on)
        btn_off = QPushButton("OFF"); btn_off.setObjectName("btnOff"); btn_off.clicked.connect(self.action_off)
        power_box.addWidget(btn_on); power_box.addWidget(btn_off); p_layout.addLayout(power_box)

        p_layout.addWidget(QLabel("COLOR LIBRARY"))
        self.grid_colors = QGridLayout()
        self.refresh_color_grid()
        p_layout.addLayout(self.grid_colors)

        action_box = QHBoxLayout()
        btn_picker = QPushButton("SELECTOR"); btn_picker.clicked.connect(self.open_picker)
        btn_save = QPushButton("SAVE COLOR"); btn_save.clicked.connect(self.save_color)
        action_box.addWidget(btn_picker); action_box.addWidget(btn_save); p_layout.addLayout(action_box)

        p_layout.addWidget(QLabel("INTENSITY"))
        self.slider = QSlider(Qt.Orientation.Horizontal); self.slider.setRange(0, 100); self.slider.setValue(100)
        self.slider.valueChanged.connect(self.apply_brightness); p_layout.addWidget(self.slider)
        layout.addWidget(self.panel)

        self.btn_exit = QPushButton("EXIT SYSTEM"); self.btn_exit.setObjectName("btnExit")
        self.btn_exit.clicked.connect(self.close_application); layout.addWidget(self.btn_exit)

        scroll.setWidget(content_widget); main_layout.addWidget(scroll); self.setCentralWidget(main_container)
        self.status = QStatusBar(); self.setStatusBar(self.status)

    def refresh_color_grid(self):
        while self.grid_colors.count():
            item = self.grid_colors.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        r, c = 0, 0
        for hex_val, name in self.custom_colors.items():
            btn_container = QPushButton()
            btn_container.setMinimumHeight(80)
            btn_container.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_container.setStyleSheet(f"""
                QPushButton {{
                    background-color: #0a0a0a;
                    border: 1px solid #1a1a1a;
                    border-radius: 12px;
                    padding: 5px;
                }}
                QPushButton:hover {{
                    border: 2px solid #{hex_val};
                    background-color: #111;
                }}
            """)
            btn_container.clicked.connect(lambda checked, h=hex_val: self.apply_hex(h))

            btn_layout = QVBoxLayout(btn_container)
            btn_layout.setContentsMargins(5, 5, 5, 5)

            # Botón de borrar (X) en esquina superior derecha
            top_row = QHBoxLayout()
            top_row.addStretch()
            btn_del = QPushButton("✕")
            btn_del.setFixedSize(18, 18)
            btn_del.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #444;
                    border: none;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    color: #ff0000;
                    background: #200000;
                    border-radius: 9px;
                }
            """)
            btn_del.clicked.connect(lambda checked, h=hex_val: self.remove_color(h))
            top_row.addWidget(btn_del)
            btn_layout.addLayout(top_row)

            # Elementos visuales
            color_circle = QLabel()
            color_circle.setFixedSize(24, 24)
            color_circle.setStyleSheet(f"background-color: #{hex_val}; border-radius: 12px; border: 1px solid #222;")
            btn_layout.addWidget(color_circle, alignment=Qt.AlignmentFlag.AlignCenter)

            name_lbl = QLabel(name[:10])
            name_lbl.setStyleSheet("color: #eee; font-size: 9px; font-weight: bold; border: none; background: transparent;")
            name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn_layout.addWidget(name_lbl)

            self.grid_colors.addWidget(btn_container, r, c)
            c += 1
            if c > 3: c = 0; r += 1

    def factory_reset(self):
        self.custom_colors = {"ff0000": "Rojo", "00ff00": "Verde", "0000ff": "Azul", "ffff00": "Amarillo", "d0f0ff": "Hielo"}
        self.save_settings(); self.refresh_color_grid(); self.check_unlock.setChecked(False)
        self.update_status("Valores por defecto restaurados.")

    def close_application(self):
        self.ble.disconnect_and_exit()
        QApplication.quit()

    def action_on(self):
        self.slider.setValue(100)
        r, g, b = self.last_rgb
        self.ble.send_burst(["7e04016401ff00ef", "7e0404f00001ff00ef", f"7e000503{r:02x}{g:02x}{b:02x}00ef"])

    def action_off(self):
        self.slider.setValue(0)
        self.ble.send_burst(["7e04010001ff00ef", "7e0004000000ff00ef", "7e07050300000010ef"])

    def apply_hex(self, h):
        self.last_rgb = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        self.ble.send_burst([f"7e000503{self.last_rgb[0]:02x}{self.last_rgb[1]:02x}{self.last_rgb[2]:02x}00ef"])

    def open_picker(self):
        c = QColorDialog.getColor(); (self.apply_hex(c.name().lstrip('#')) if c.isValid() else None)

    def save_color(self):
        name, ok = QInputDialog.getText(self, "Nuevo Perfil", "Nombre del color:")
        if ok and name:
            h = f"{self.last_rgb[0]:02x}{self.last_rgb[1]:02x}{self.last_rgb[2]:02x}"
            self.custom_colors[h] = name
            self.save_settings(); self.refresh_color_grid()

    def remove_color(self, h):
        if h in self.custom_colors:
            del self.custom_colors[h]; self.save_settings(); self.refresh_color_grid()

    def apply_brightness(self):
        v = self.slider.value(); self.ble.send_burst([f"7e0001{v:02x}00000000ef", f"7e0401{v:02x}01ff00ef"])

    def start_scan(self):
        if self.ask_pwd_if_needed():
            threading.Thread(target=self._manual_scan, daemon=True).start()

    def _manual_scan(self):
        self.update_status("Buscando...")
        try:
            cmd = f"echo '{self.sudo_password}' | sudo -S bluetoothctl devices | grep -i 'ELK-BLEDOM'"
            res = subprocess.check_output(cmd, shell=True, text=True)
            devs = [line.split(' ', 2)[1:3] for line in res.strip().split('\n') if line]
            self.list_ui.clear()
            for mac, name in devs: self.list_ui.addItem(f"{name} | {mac}")
        except: self.update_status("Error en escaneo.")

    def init_connection(self):
        item = self.list_ui.currentItem()
        if item and self.ask_pwd_if_needed():
            self.ble.connect(item.text().split(" | ")[1], self.sudo_password)

    def on_connection_change(self, s): self.panel.setEnabled(s)
    def update_status(self, m): self.status.showMessage(m)
    def save_settings(self):
        with open(CONFIG_FILE, 'w') as f: json.dump(self.custom_colors, f)

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion"); win = MITLedControl(); win.show(); sys.exit(app.exec())
