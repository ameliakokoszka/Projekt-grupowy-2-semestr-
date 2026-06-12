import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QLineEdit, QSpinBox,
    QFrame, QProgressBar, QScrollArea, QComboBox, QListView
)

class KalkulatorPunktow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Kalkulator Punktow Studenckich")
        self.setGeometry(100, 100, 620, 720)

        self.dane_przedmiotow: dict = {}

        self.spinboxy: dict = {}
        self.wiersze_form_zaliczenia: list = []

        self.stos = QStackedWidget()
        self.setCentralWidget(self.stos)

        self.strona_glowna = QWidget()
        self.strona_glowna.setObjectName("strona")

        self.strona_przedmiotu = QWidget()
        self.strona_przedmiotu.setObjectName("strona")

        self.strona_dodawania = QWidget()
        self.strona_dodawania.setObjectName("strona")

        self._buduj_glowna()
        self._buduj_przedmiot()
        self._buduj_dodawanie()

        self.stos.addWidget(self.strona_glowna)      
        self.stos.addWidget(self.strona_przedmiotu)  
        self.stos.addWidget(self.strona_dodawania)   

        self._ustaw_style()

        self._pokaz_dodawanie()
