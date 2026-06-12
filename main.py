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

#Strona przedmiotu

    def _buduj_przedmiot(self) -> None:
        uklad = QVBoxLayout(self.strona_przedmiotu)
        uklad.setContentsMargins(0, 0, 0, 0)
        uklad.setSpacing(0)

        pasek = QWidget()
        pasek.setObjectName("pasekGorny")

        pu = QHBoxLayout(pasek)
        pu.setContentsMargins(16, 14, 24, 14)

        btn_w = QPushButton("← Powrot")
        btn_w.setObjectName("btnWstecz")
        btn_w.clicked.connect(self._pokaz_glowna)
        pu.addWidget(btn_w)

        pu.addStretch()

        self.etykieta_tytul = QLabel("")
        self.etykieta_tytul.setObjectName("tytulPrzedmiotu")
        pu.addWidget(self.etykieta_tytul)

        pu.addStretch()

        pusty = QWidget()
        pusty.setFixedWidth(90)
        pu.addWidget(pusty)

        uklad.addWidget(pasek)

        tresc = QWidget()
        tresc.setObjectName("contentArea")

        tu = QVBoxLayout(tresc)
        tu.setContentsMargins(24, 24, 24, 24)
        tu.setSpacing(16)

        self.form_frame_punkty = QFrame()
        self.form_frame_punkty.setObjectName("formFrame")

        self.uklad_punktow = QVBoxLayout(self.form_frame_punkty)
        self.uklad_punktow.setContentsMargins(20, 16, 20, 18)
        self.uklad_punktow.setSpacing(14)

        tu.addWidget(self.form_frame_punkty)

        btn_przelicz = QPushButton("Przelicz punkty")
        btn_przelicz.setObjectName("btnPrzelicz")
        btn_przelicz.clicked.connect(self._przelicz)
        tu.addWidget(btn_przelicz)

        self.etykieta_wyniku = QLabel("")
        self.etykieta_wyniku.setAlignment(Qt.AlignCenter)
        self.etykieta_wyniku.setWordWrap(True)
        self.etykieta_wyniku.setMinimumHeight(80)
        tu.addWidget(self.etykieta_wyniku)

        tu.addStretch()
        uklad.addWidget(tresc)

    def _zbuduj_pola_punktow(self, nazwa_przedmiotu: str) -> None:
        while self.uklad_punktow.count():
            item = self.uklad_punktow.takeAt(0)

            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._wyczysc_layout(item.layout())

        self.spinboxy = {}

        sekcja_tytul = QLabel("Wpisz zdobyte punkty")
        sekcja_tytul.setObjectName("sekcjaTytul")
        self.uklad_punktow.addWidget(sekcja_tytul)

        linia = QFrame()
        linia.setFrameShape(QFrame.HLine)
        linia.setStyleSheet(
            "color: #E8D8FF; background: #E8D8FF; max-height:1px; border:none;"
        )
        self.uklad_punktow.addWidget(linia)
        elementy = self.dane_przedmiotow[nazwa_przedmiotu]["elementy"]
        for element in elementy:
            nazwa = element["nazwa"]
            maks = element["maks"]

            wiersz = QHBoxLayout()

            etykieta = QLabel(
                f"{nazwa}  <span style='color:#9B8AAB;font-size:12px'>(0–{maks} pkt)</span>"
            )
            etykieta.setObjectName("formLabel")
            etykieta.setTextFormat(Qt.RichText)

            spin = QSpinBox()
            spin.setRange(0, maks)
            spin.setFixedWidth(90)

            self.spinboxy[nazwa] = spin

            wiersz.addWidget(etykieta)
            wiersz.addStretch()
            wiersz.addWidget(spin)

            self.uklad_punktow.addLayout(wiersz)

    def _przelicz(self) -> None:
        suma = sum(s.value() for s in self.spinboxy.values())
        nazwa = self.etykieta_tytul.text()

        if nazwa not in self.dane_przedmiotow:
            return

        prog = self.dane_przedmiotow[nazwa]["prog"]
        self.dane_przedmiotow[nazwa]["zdobyte"] = suma

        if suma >= prog:
            tekst = f"Zaliczone!\nMasz lacznie {suma} pkt"
            kolor, tlo = "#1A7A2A", "#D4F0D4"
        else:
            tekst = f"Brakuje Ci jeszcze {prog - suma} pkt\nMasz {suma} pkt  •  Prog: {prog} pkt"
            kolor, tlo = "#6A3D9E", "#EEE5FF"

        self.etykieta_wyniku.setText(tekst)
        self.etykieta_wyniku.setStyleSheet(f"""
            color: {kolor};
            font-size: 15px;
            font-weight: 700;
            background-color: {tlo};
            border-radius: 14px;
            padding: 18px;
            border: none;
        """)

