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
#Strona główna

    def _buduj_glowna(self) -> None:
        uklad = QVBoxLayout(self.strona_glowna)
        uklad.setContentsMargins(0, 0, 0, 0)
        uklad.setSpacing(0)

        pasek = QWidget()
        pasek.setObjectName("pasekGorny")

        pu = QHBoxLayout(pasek)
        pu.setContentsMargins(24, 18, 24, 18)

        tytul = QLabel("Moje przedmioty")
        tytul.setObjectName("tytulApki")
        pu.addWidget(tytul)

        pu.addStretch()

        btn = QPushButton("+ Dodaj przedmiot")
        btn.setObjectName("btnDodaj")
        btn.clicked.connect(self._pokaz_dodawanie)
        pu.addWidget(btn)

        uklad.addWidget(pasek)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setObjectName("mainScroll")

        self.kontener = QWidget()
        self.kontener.setObjectName("scrollKontener")

        self.uklad_kart = QVBoxLayout(self.kontener)
        self.uklad_kart.setContentsMargins(24, 24, 24, 24)
        self.uklad_kart.setSpacing(18)
        self.uklad_kart.setAlignment(Qt.AlignTop)

        scroll.setWidget(self.kontener)
        uklad.addWidget(scroll)

        self._odswiez_karty()

    def _odswiez_karty(self) -> None:
        while self.uklad_kart.count():
            item = self.uklad_kart.takeAt(0)

            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._wyczysc_layout(item.layout())

        kolory = ["#FDEAF1", "#FFF8D6", "#EEE5FF", "#DFF7F0", "#FFE8D6"]

        for i, (nazwa, dane) in enumerate(self.dane_przedmiotow.items()):
            self.uklad_kart.addWidget(
                self._zrob_karte(nazwa, dane, kolory[i % len(kolory)])
            )

    def _zrob_karte(self, nazwa: str, dane: dict, kolor: str) -> QFrame:
        karta = QFrame()
        karta.setStyleSheet(f"""
            QFrame {{
                background-color: {kolor};
                border-radius: 18px;
                border: 1.5px solid rgba(0,0,0,0.06);
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        u = QVBoxLayout(karta)
        u.setContentsMargins(22, 18, 22, 18)
        u.setSpacing(10)

        nagl = QLabel(nazwa)
        nagl.setObjectName("nazwaKarty")
        u.addWidget(nagl)

        zdobyte = dane["zdobyte"]
        maks = dane["maks"]
        prog = dane["prog"]

        pasek = QProgressBar()
        pasek.setMaximum(maks)
        pasek.setValue(zdobyte)
        pasek.setTextVisible(False)
        pasek.setFixedHeight(12)

        kolor_paska = "#88C98A" if zdobyte >= prog else "#C9A8E0"

        pasek.setStyleSheet(f"""
            QProgressBar {{
                background: rgba(255,255,255,0.65);
                border-radius: 6px;
                border: none;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {kolor_paska},
                    stop:1 {'#5AAB5C' if zdobyte >= prog else '#9B72C4'});
                border-radius: 6px;
            }}
        """)

        u.addWidget(pasek)

        wiersz = QHBoxLayout()

        info = QLabel(f"{zdobyte} / {maks} pkt  •  Prog: {prog} pkt")
        info.setObjectName("infoKarty")
        wiersz.addWidget(info)

        wiersz.addStretch()

        if zdobyte >= prog:
            st = QLabel("Zaliczone!")
            st.setStyleSheet(
                "color:#1A7A2A; font-weight:700; font-size:12px; background:transparent;"
            )
        else:
            brakuje = prog - zdobyte
            st = QLabel(f"Brakuje: {brakuje} pkt")
            st.setStyleSheet(
                "color:#6A3D9E; font-weight:700; font-size:12px; background:transparent;"
            )

        wiersz.addWidget(st)
        u.addLayout(wiersz)

        btn = QPushButton("Otworz szczegoly  →")
        btn.setObjectName("btnOtworzKarte")
        btn.clicked.connect(lambda checked=False, n=nazwa: self._pokaz_przedmiot(n))
        u.addWidget(btn)

        return karta
