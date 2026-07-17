
import sys
import threading

from PySide6.QtWidgets import QWidget, QApplication, QPushButton, QMessageBox
from PySide6.QtGui import Qt,QFont
from PySide6.QtCore import Signal
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from state_management import load_config, get_base_dir,save_config
from run_energy_saver import run_energy_toggle

SERVER_NAME = "EnergySaverSingleton"

class windows11energysaverswitch(QWidget):
    toggle_complete = Signal(bool, str)

    def __init__(self):
        super().__init__()
        self.toggle_lock = threading.Lock()

        self.setWindowTitle("Windows Energy Saver Switch")
        self.setFixedSize(200, 100)

        QLocalServer.removeServer(SERVER_NAME)
        self.server = QLocalServer(self)
        self.server.listen(SERVER_NAME)
        self.server.newConnection.connect(self.handle_activation)

        self.button = QPushButton(self)
        self.button.setFont(QFont("Rubik", 11))
        self.button.move(25, 25)
        self.button.setFixedSize(150, 50)
        self.button.setCheckable(True)

        self.base_dir = get_base_dir().resolve()
        self.config_path = (self.base_dir / "config.json").resolve()
        self.script = (self.base_dir / "EnergySaver.ahk").resolve()

        self.config = load_config(self.config_path)

        # ----- init state WITHOUT firing handlers -----
        initial_eco = bool(self.config.get("eco_mode", False))
        self.confirmed_eco = initial_eco
        self.pending_eco = initial_eco
        self.is_switching = False

        self.button.blockSignals(True)
        self.button.setChecked(initial_eco)
        self.button.blockSignals(False)
        self.button_visual_update(initial_eco)

        self.button.toggled.connect(self.on_mode_changed)
        self.toggle_complete.connect(self.on_toggle_complete)
        
    def on_mode_changed(self, eco: bool):
        if self.is_switching:
            return

        self.is_switching = True
        self.pending_eco = eco
        self.button_visual_update(eco)
        self.button.setEnabled(False)
        threading.Thread(
            target=self.run_energy_toggle_background,
            args=(eco,),
            daemon=True,
        ).start()

    def run_energy_toggle_background(self, eco: bool):
        with self.toggle_lock:
            success, message = run_energy_toggle(eco)
        self.toggle_complete.emit(success, message)

    def on_toggle_complete(self, success: bool, message: str):
        self.is_switching = False
        self.button.setEnabled(True)

        if not success:
            self.button.blockSignals(True)
            self.button.setChecked(self.confirmed_eco)
            self.button.blockSignals(False)
            self.button_visual_update(self.confirmed_eco)
            QMessageBox.warning(self, "Energy Saver not changed", message)
            return

        self.confirmed_eco = self.pending_eco
        self.config["eco_mode"] = self.confirmed_eco
        try:
            save_config(self.config_path, self.config)
        except OSError as error:
            QMessageBox.warning(
                self,
                "Energy Saver changed, but state was not saved",
                f"Windows accepted the change, but config.json could not be updated.\n\n{error}",
            )
            return

        QApplication.instance().quit()

    def button_visual_update(self, eco: bool):
        self.button.setText("Eco Mode" if eco else "Normal Mode")

    def handle_activation(self):
        socket = self.server.nextPendingConnection()
        if socket:
            socket.readAll()

        self.showNormal()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized)
        self.activateWindow()
        self.raise_()

if __name__ == "__main__":
    app = QApplication()

    socket = QLocalSocket()
    socket.connectToServer(SERVER_NAME)

    if socket.waitForConnected(100):
        socket.write(b"activate")
        socket.flush()
        socket.waitForBytesWritten(100)
        sys.exit(0)

    window = windows11energysaverswitch()
    window.show()
    app.exec()
