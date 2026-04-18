
from pathlib import Path
import sys

from PySide6.QtWidgets import QWidget,QApplication,QPushButton, QSystemTrayIcon,QMenu
from PySide6.QtGui import QIcon, QAction,Qt,QFont
from PySide6.QtCore import QTimer
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from state_management import load_config, get_base_dir,save_config
from run_energy_saver import run_energy_toggle

SERVER_NAME = "EnergySaverSingleton"

class windows11energysaverswitch(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Windows Energy Saver Switch")
        self.setFixedSize(200, 100)

        QLocalServer.removeServer(SERVER_NAME)
        self.server = QLocalServer(self)
        self.server.listen(SERVER_NAME)
        self.server.newConnection.connect(self.handle_activation)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_app_from_tray)

        self.tray = QSystemTrayIcon(self)
        base_dir = Path(__file__).parent
        icon_path = base_dir / "energyleaf.ico"

        menu = QMenu()
        menu.addAction(exit_action)
        self.tray.setContextMenu(menu)
        self.tray.setIcon(QIcon(str(icon_path)))
        self.tray.setVisible(True)
        self.tray.activated.connect(self.on_tray_activated)

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
        run_energy_toggle(eco)
        
            # hide AFTER logic runs
        QTimer.singleShot(150, self.hide)

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

    def on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            if self.isVisible():
                self.hide()
            else:
                self.showNormal()
                self.setWindowState(self.windowState() & ~Qt.WindowMinimized)
                self.activateWindow()
                self.raise_()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def exit_app_from_tray(self):
        QApplication.quit()

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
