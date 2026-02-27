
from pathlib import Path
import sys

from PySide6.QtWidgets import QWidget,QApplication,QPushButton, QSystemTrayIcon,QMenu
from PySide6.QtGui import QIcon, QAction,Qt 
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from state_management import load_config, get_base_dir,save_config
from run_energy_saver import run_energy_toggle

SERVER_NAME = "EnergySaverSingleton"

class windows11energysaverswitch(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Windows Energy Saver Switch")
        self.setFixedSize(200,100)

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
        self.tray.setContextMenu(menu)
        menu.addAction(exit_action)
    
        self.tray.setIcon(QIcon(str(icon_path)))
        self.tray.setVisible(True)

        self.button = QPushButton(self)
        self.button.setFont("Rubik")
        self.button.move(25,25)
        self.button.setFixedSize(150,50)
        self.button.setCheckable(True)
        
        self.button.clicked.connect(run_energy_toggle)
        self.button.toggled.connect(self.button_visual_update)
        self.tray.activated.connect(self.on_tray_activated)
    
        self.base_dir = get_base_dir().resolve()

        self.config_path = (self.base_dir / "config.json").resolve()
        self.script = (self.base_dir / "EnergySaver.ahk").resolve()

    
        self.config = load_config(self.config_path)
        
        self.button.setChecked(self.config["eco_mode"])
        self.button.clicked.connect(self.hide)
        self.button_visual_update()
    
    def button_visual_update(self):

        eco = self.button.isChecked()

        if eco:
            self.button.setText("Eco Mode")
        else:
            self.button.setText("Normal Mode")

        self.config["eco_mode"] = eco
        save_config(self.config_path, self.config)


    def handle_activation(self):

        socket = self.server.nextPendingConnection()
        if socket:
            socket.readAll()

        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized)
        self.activateWindow()
        self.raise_()


    def on_tray_activated(self, reason):
        if reason in (
            QSystemTrayIcon.Trigger,      # single click
            QSystemTrayIcon.DoubleClick   # double click
        ):

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
    app.setOrganizationName("main")
    app.setApplicationName("main")
    
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