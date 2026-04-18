
import sys
import threading

from PySide6.QtWidgets import QWidget,QApplication,QPushButton
from PySide6.QtGui import Qt,QFont
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from state_management import load_config, get_base_dir,save_config
from run_energy_saver import run_energy_toggle

SERVER_NAME = "EnergySaverSingleton"

class windows11energysaverswitch(QWidget):
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
    

        self.button.blockSignals(True)
        self.button.setChecked(initial_eco)
        self.button.blockSignals(False)
        self.button_visual_update(initial_eco)

        self.button.toggled.connect(self.on_mode_changed)
        
    def on_mode_changed(self, eco: bool):
        print("TOGGLE FIRED:", eco)
        self.button_visual_update(eco)
        self.config["eco_mode"] = eco
        save_config(self.config_path, self.config)
        threading.Thread(
            target=self.run_energy_toggle_background,
            args=(eco,),
            daemon=True,
        ).start()

    def run_energy_toggle_background(self, eco: bool):
        with self.toggle_lock:
            run_energy_toggle(eco)

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
