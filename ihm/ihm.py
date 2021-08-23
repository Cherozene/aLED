#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from shutil import copyfile
import configparser
import serial.tools.list_ports

from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QLineEdit, QComboBox, \
                            QGridLayout, QPlainTextEdit, QMainWindow, QApplication

BAUDRATES = ['300', '600', '1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200']

# TODO : mode cinéma / gestion bandes noires
# TODO : dans l'IHM un menu dédié pour régler tous les paramètres du fichier de config, qui est utilisé par les scripts

# on recopie le fichier de config par défaut ; l'IHM travaille sur cette copie locale
copyfile('scripts\\default_config.ini', 'scripts\\config.ini')

class AmbilightIHM(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mode = 'off' # 0 : off, 1 : screenlight, 2 : cinéma, 3 : ambilight
        self.p = None # plus tard utilisé pour le process
        self.avail_comports = [port.name+' '+port.description for port in serial.tools.list_ports.comports()]
        
        self.setupUi()


    def setupUi(self):
        self.setWindowTitle("Ambilight IHM")
        self.setStyleSheet("background-color: black;")
        self.resize(400, 500)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)


        # title widget
        self.titleLabel = QLabel("Screen Ambilight Control")
        self.titleLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.titleLabel.setStyleSheet("color: white; font: 24pt;")


        # mode widget
        self.modeLabel = QLabel(f"Mode actuel : {self.mode}", self)
        self.modeLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.modeLabel.setStyleSheet("color: white; font: 16pt;")


        # colors widgets
        self.colorLabel = QLabel("RGB pour mode fixe (0 - 255)")
        self.colorLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.colorLabel.setStyleSheet("color: white;")

        self.redbox = QLineEdit(self)
        self.redbox.setText('R')
        self.redbox.setStyleSheet("color: white;")
        self.redbox.setMaxLength(3)
        self.greenbox = QLineEdit(self)
        self.greenbox.setText('G')
        self.greenbox.setStyleSheet("color: white;")
        self.greenbox.setMaxLength(3)
        self.bluebox = QLineEdit(self)
        self.bluebox.setText('B')
        self.bluebox.setStyleSheet("color: white;")
        self.bluebox.setMaxLength(3)


        # COM ports widgets
        self.comportLabel = QLabel("Sélection du port COM")
        self.comportLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.comportLabel.setStyleSheet("color: white;")

        self.menu_comports = QComboBox(self)
        self.menu_comports.setStyleSheet("background-color: grey;")
        self.menu_comports.addItems(self.avail_comports)
        self.menu_comports.currentTextChanged.connect(self.update_comport)

        # Baudrate widgets
        self.baudrateLabel = QLabel("Sélection du baudrate")
        self.baudrateLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.baudrateLabel.setStyleSheet("color: white;")

        self.menu_baudrates = QComboBox(self)
        self.menu_baudrates.setStyleSheet("background-color: grey;")
        self.menu_baudrates.addItems(BAUDRATES)
        self.menu_baudrates.currentTextChanged.connect(self.update_baudrate)


        # buttons widgets
        self.button_off = QPushButton("Eteindre les lumières", self)
        self.button_off.setStyleSheet("background-color: grey;")
        self.button_off.clicked.connect(self.push_button_off)

        self.button_screenlight = QPushButton("Mode suivi d'écran", self)
        self.button_screenlight.setStyleSheet("background-color: grey;")
        self.button_screenlight.clicked.connect(self.push_button_screenlight)

        self.button_cinema = QPushButton("Mode suivi d'écran cinéma", self)
        self.button_cinema.setStyleSheet("background-color: grey;")
        self.button_cinema.clicked.connect(self.push_button_cinema)

        self.button_ambilight = QPushButton("Mode couleur fixe", self)
        self.button_ambilight.setStyleSheet("background-color: grey;")
        self.button_ambilight.clicked.connect(self.push_button_ambilight)


        # info text widget
        self.infoLabel = QLabel("Info :")
        self.infoLabel.setStyleSheet("color: white;")
        self.text = QPlainTextEdit()
        self.text.setStyleSheet("color: white;")
        self.text.setReadOnly(True)


        # Set the layout
        layout = QGridLayout()

        layout.addWidget(self.titleLabel, 0, 0, 1, 3)

        layout.addWidget(self.colorLabel, 1, 0)
        layout.addWidget(self.redbox, 2, 0)
        layout.addWidget(self.greenbox, 3, 0)
        layout.addWidget(self.bluebox, 4, 0)

        layout.addWidget(self.comportLabel, 1, 1)
        layout.addWidget(self.menu_comports, 2, 1)
        layout.addWidget(self.baudrateLabel, 3, 1)
        layout.addWidget(self.menu_baudrates, 4, 1)

        layout.addWidget(self.modeLabel, 5, 0, 1, 3)

        layout.addWidget(self.button_off, 7, 0, 1, 3)
        layout.addWidget(self.button_screenlight, 8, 0, 1, 3)
        layout.addWidget(self.button_cinema, 9, 0, 1, 3)
        layout.addWidget(self.button_ambilight, 10, 0, 1, 3)

        layout.addWidget(self.infoLabel, 11, 0)
        layout.addWidget(self.text, 12, 0, 1, 3)
        self.centralWidget.setLayout(layout)


    def push_button_off(self):
        self.reset_process() # pour tuer le process en cours si besoin
        self.mode = 'off'
        self.modeLabel.setText(f"Mode actuel : {self.mode}")
        self.p.start("python", ["scripts\\ambi_fixe.py", '0', '0', '0'])
        self.message("On éteint tout !")

    def push_button_screenlight(self):
        self.reset_process() # pour tuer le process en cours si besoin
        self.mode = 'screenlight'
        self.modeLabel.setText(f"Mode actuel : {self.mode}")
        self.p.start("python", ["scripts\\screencap.py"])
        self.message("Ambilight dynamique (mode full écran)")

    def push_button_cinema(self):
        self.reset_process() # pour tuer le process en cours si besoin
        self.mode = 'cinema'
        self.modeLabel.setText(f"Mode actuel : {self.mode}")
        # TODO : idem à la fonction screencap, mais en changeant les macros pour ne pas traiter les bandes noires
        self.message("[EN CHANTIER] Ambilight dynamique (mode cinéma)")

    def push_button_ambilight(self):
        self.reset_process() # pour tuer le process en cours si besoin

        try:
            red = int(self.redbox.text())
            green = int(self.greenbox.text())
            blue = int(self.bluebox.text())
        except:
            self.message("[ERREUR] Les couleurs doivent être des nombres entre 0 et 255.")
            return

        if (red < 0 or red > 255) or (green < 0 or green > 255) or (blue < 0 or blue > 255):
            self.message("[ERREUR] Les couleurs doivent être des nombres entre 0 et 255.")
        else:
            self.mode = 'ambilight'
            self.modeLabel.setText(f"Mode actuel : {self.mode}")
            self.p.start("python", ["scripts\\ambi_fixe.py", str(red), str(green), str(blue)])
            self.message("Ambilight couleur fixe {}, {}, {}".format(red, green, blue))

    def reset_process(self):
        if self.p is not None:
            self.p.kill()
            self.p = None
        self.p = QProcess()
        self.p.readyReadStandardOutput.connect(self.handle_stdout)
        self.p.readyReadStandardError.connect(self.handle_stderr)
        self.p.stateChanged.connect(self.handle_state)

    def update_comport(self, s):
        conffile = configparser.ConfigParser()
        conffile.read('scripts\\config.ini')
        conffile['LIEN_SERIE']['COMPort'] = s[:4]
        with open('scripts\\config.ini', 'w') as filename:
            conffile.write(filename)
        self.message("COM port set to: {}".format(s[:4]))

    def update_baudrate(self, s):
        conffile = configparser.ConfigParser()
        conffile.read('scripts\\config.ini')
        conffile['LIEN_SERIE']['Baudrate'] = s
        with open('scripts\\config.ini', 'w') as filename:
            conffile.write(filename)
        self.message("Baudrate set to: {}".format(s))

    def message(self, s):
        self.text.appendPlainText(s)
        
    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode('utf-8')
        self.message(stdout)

    def handle_stderr(self):
        data = self.p.readAllStandardError()
        print(data)
        stderr = bytes(data).decode('utf-8')
        self.message(stderr)

    def handle_state(self, state):
        states = {
            QProcess.NotRunning: 'Not running',
            QProcess.Starting: 'Starting',
            QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.message("State changed: {}".format(state_name))


app = QApplication(sys.argv)
win = AmbilightIHM()
win.show()
app.exec()

# TODO : effacer le fichier de config temporaire

print('Closing')