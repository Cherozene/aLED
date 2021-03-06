#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from os import remove
from shutil import copyfile
import configparser
import serial.tools.list_ports

from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtWidgets import QSlider, QWidget, QLabel, QPushButton, QLineEdit, QComboBox, \
                            QGridLayout, QMainWindow, QApplication

BAUDRATES = ['9600', '19200', '38400', '57600', '115200', '230400']

# TODO : dans l'IHM un menu dédié pour régler tous les paramètres du fichier de config, qui est utilisé par les scripts

# on recopie le fichier de config par défaut ; l'IHM travaille sur cette copie locale
copyfile('scripts\\default_config.ini', 'scripts\\config.ini')

class LedCC(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mode = 'off' # off, screenlight, unicolor, minuteur
        self.p = None # plus tard utilisé pour le process
        self.avail_comports = [port.name+' '+port.description for port in serial.tools.list_ports.comports()]
        
        self.setupUi()


    def setupUi(self):
        self.setWindowTitle("LEDs Control Center")
        self.setStyleSheet("background-color: black;")
        self.resize(400, 400)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)


        # title widget
        self.titleLabel = QLabel("LEDs Control Center")
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

        # luminosity slider
        self.lum_label = QLabel("Luminosité pour mode fixe", self)
        self.lum_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.lum_label.setStyleSheet("color: white;")

        self.lum_slider = QSlider(Qt.Horizontal, self)
        self.lum_slider.setGeometry(30, 40, 200, 30)
        self.lum_slider.setRange(0, 100)
        self.lum_slider.setValue(100)
        self.lum_slider.setTickPosition(QSlider.TicksBelow)
        self.lum_slider.setTickInterval(10)
        self.lum_slider.valueChanged[int].connect(self.luminosity_update)

        # buttons widgets
        self.button_off = QPushButton("Eteindre les lumières", self)
        self.button_off.setStyleSheet("background-color: grey;")
        self.button_off.clicked.connect(self.push_button_off)

        self.button_screenlight = QPushButton("Suivi d'écran", self)
        self.button_screenlight.setStyleSheet("background-color: grey;")
        self.button_screenlight.clicked.connect(self.push_button_screenlight)

        self.button_unicolor = QPushButton("Couleur unie et fixe", self)
        self.button_unicolor.setStyleSheet("background-color: grey;")
        self.button_unicolor.clicked.connect(self.push_button_unicolor)

        self.button_timer = QPushButton("Minuteur", self)
        self.button_timer.setStyleSheet("background-color: grey;")
        self.button_timer.clicked.connect(self.push_button_timer)

        # minuteur widgets
        self.timerLabel = QLabel("Réglage du minuteur (minutes et secondes)")
        self.timerLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.timerLabel.setStyleSheet("color: white;")

        self.minutesbox = QLineEdit(self)
        self.minutesbox.setText('minutes')
        self.minutesbox.setStyleSheet("color: white;")
        self.minutesbox.setMaxLength(3)
        self.secondsbox = QLineEdit(self)
        self.secondsbox.setText('secondes')
        self.secondsbox.setStyleSheet("color: white;")
        self.secondsbox.setMaxLength(3)

        # info text widget
        self.infoLabel = QLabel("Info :")
        self.infoLabel.setStyleSheet("color: white;")
        self.text = QLineEdit()
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

        layout.addWidget(self.lum_label, 5, 0, 1, 3)
        layout.addWidget(self.lum_slider, 6, 0, 1, 3)

        layout.addWidget(self.modeLabel, 7, 0, 1, 3)

        layout.addWidget(self.button_off, 9, 0, 1, 3)
        layout.addWidget(self.button_screenlight, 10, 0, 1, 3)
        layout.addWidget(self.button_unicolor, 11, 0, 1, 3)

        layout.addWidget(self.timerLabel, 12, 0, 1, 3)
        layout.addWidget(self.minutesbox, 13, 0)
        layout.addWidget(self.secondsbox, 13, 1)
        layout.addWidget(self.button_timer, 14, 0, 1, 3)

        layout.addWidget(self.infoLabel, 15, 0)
        layout.addWidget(self.text, 16, 0, 1, 3)
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
        self.message("Suivi d'écran")

    def push_button_unicolor(self):
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
            self.mode = 'unicolor'
            self.modeLabel.setText(f"Mode actuel : {self.mode}")
            self.p.start("python", ["scripts\\ambi_fixe.py", str(red), str(green), str(blue)])
            self.message("Couleur unie et fixe {}, {}, {}".format(red, green, blue))

    def push_button_timer(self):
        self.reset_process() # pour tuer le process en cours si besoin

        try:
            minutes = int(self.minutesbox.text())
            seconds = int(self.secondsbox.text())
        except:
            self.message("[ERREUR] Les minutes et secondes doivent être des entiers.")
            return

        if (minutes < 0) or (seconds < 0 or seconds > 59):
            self.message("[ERREUR] Les minutes doivent être positives. Les secondes de 0 à 59. Valeurs entières.")
        else:
            self.mode = 'minuteur'
            self.modeLabel.setText(f"Mode actuel : {self.mode}")
            import time
            print(time.time())
            self.p.start("python", ["scripts\\timer.py", str(60*minutes+seconds)])
            self.message("Minuteur démarré pour {} minute(s) et {} seconde(s).".format(minutes, seconds))

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

    def luminosity_update(self, lum):
        conffile = configparser.ConfigParser()
        conffile.read('scripts\\config.ini')
        conffile['LEDS']['Luminosity'] = str(lum)
        with open('scripts\\config.ini', 'w') as filename:
            conffile.write(filename)
        self.message("Luminosity set to: {}%".format(lum))

    def message(self, s):
        self.text.setText(s)
        
    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode()
        self.message(stdout)

    def handle_stderr(self):
        data = self.p.readAllStandardError()
        print(data)
        stderr = bytes(data).decode()
        self.message(stderr)

    def handle_state(self, state):
        states = {
            QProcess.NotRunning: 'Not running',
            QProcess.Starting: 'Starting',
            QProcess.Running: 'Running',
        }
        state_name = states[state]
        #self.message("State changed: {}".format(state_name))


app = QApplication(sys.argv)
win = LedCC()
win.show()
app.exec()

#remove temporary config file
remove('scripts\\config.ini')

print('Closing')