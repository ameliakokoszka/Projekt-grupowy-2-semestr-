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
#Strona dodawania
def _buduj_dodawanie(self) -> None:
        uklad = QVBoxLayout(self.strona_dodawania)
        uklad.setContentsMargins(0, 0, 0, 0)
        uklad.setSpacing(0)

        pasek = QWidget()
        pasek.setObjectName("pasekGorny")

        pu = QHBoxLayout(pasek)
        pu.setContentsMargins(16, 14, 24, 14)

        btn_w = QPushButton("← Powrot")
        btn_w.setObjectName("btnWstecz")
        btn_w.clicked.connect(self._powrot_z_dodawania)
        pu.addWidget(btn_w)

        pu.addStretch()

        self.tytul_dodawania = QLabel("Dodaj pierwszy przedmiot")
        self.tytul_dodawania.setObjectName("tytulPrzedmiotu")
        pu.addWidget(self.tytul_dodawania)

        pu.addStretch()

        pusty = QWidget()
        pusty.setFixedWidth(90)
        pu.addWidget(pusty)

        uklad.addWidget(pasek)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        tresc = QWidget()
        tresc.setObjectName("contentArea")

        tu = QVBoxLayout(tresc)
        tu.setContentsMargins(24, 24, 24, 24)
        tu.setSpacing(16)

        form_frame = QFrame()
        form_frame.setObjectName("formFrame")

        fl = QVBoxLayout(form_frame)
        fl.setContentsMargins(20, 18, 20, 20)
        fl.setSpacing(14)

        nagl = QLabel("Dane przedmiotu")
        nagl.setObjectName("sekcjaTytul")
        fl.addWidget(nagl)

        linia = QFrame()
        linia.setFrameShape(QFrame.HLine)
        linia.setStyleSheet(
            "color: #E8D8FF; background: #E8D8FF; max-height:1px; border:none;"
        )
        fl.addWidget(linia)

        et1 = QLabel("Nazwa przedmiotu:")
        et1.setObjectName("formLabel")
        fl.addWidget(et1)

        self.pole_nazwa = QLineEdit()
        self.pole_nazwa.setPlaceholderText("np. Matematyka Dyskretna")
        fl.addWidget(self.pole_nazwa)

        et2 = QLabel("Prog zaliczenia:")
        et2.setObjectName("formLabel")
        fl.addWidget(et2)

        self.pole_prog = QSpinBox()
        self.pole_prog.setRange(0, 9999)
        self.pole_prog.setValue(51)
        self.pole_prog.setSuffix(" pkt")
        fl.addWidget(self.pole_prog)

        tu.addWidget(form_frame)

        warunki_frame = QFrame()
        warunki_frame.setObjectName("formFrame")

        self.uklad_warunkow = QVBoxLayout(warunki_frame)
        self.uklad_warunkow.setContentsMargins(20, 18, 20, 20)
        self.uklad_warunkow.setSpacing(14)

        nagl2 = QLabel("Warunki zaliczenia")
        nagl2.setObjectName("sekcjaTytul")
        self.uklad_warunkow.addWidget(nagl2)

        opis = QLabel(
        )
        opis.setWordWrap(True)
        opis.setObjectName("infoKarty")
        self.uklad_warunkow.addWidget(opis)

        linia2 = QFrame()
        linia2.setFrameShape(QFrame.HLine)
        linia2.setStyleSheet(
            "color: #E8D8FF; background: #E8D8FF; max-height:1px; border:none;"
        )
        self.uklad_warunkow.addWidget(linia2)

        self.lista_warunkow_widget = QWidget()
        self.lista_warunkow_layout = QVBoxLayout(self.lista_warunkow_widget)
        self.lista_warunkow_layout.setContentsMargins(0, 0, 0, 0)
        self.lista_warunkow_layout.setSpacing(12)

        self.uklad_warunkow.addWidget(self.lista_warunkow_widget)

        btn_dodaj_warunek = QPushButton("+ Dodaj element zaliczenia")
        btn_dodaj_warunek.setObjectName("btnOtworzKarte")
        btn_dodaj_warunek.clicked.connect(self._dodaj_wiersz_formy_zaliczenia)
        self.uklad_warunkow.addWidget(btn_dodaj_warunek)

        tu.addWidget(warunki_frame)

        btn_zap = QPushButton("Zapisz przedmiot")
        btn_zap.setObjectName("btnPrzelicz")
        btn_zap.clicked.connect(self._zapisz_przedmiot)
        tu.addWidget(btn_zap)

        tu.addStretch()

        scroll.setWidget(tresc)
        uklad.addWidget(scroll)

        self._dodaj_wiersz_formy_zaliczenia()

    def _dodaj_wiersz_formy_zaliczenia(self) -> None:
        wiersz_widget = QFrame()
        wiersz_widget.setObjectName("wierszWarunku")

        wiersz_glowny = QVBoxLayout(wiersz_widget)
        wiersz_glowny.setContentsMargins(12, 12, 12, 12)
        wiersz_glowny.setSpacing(8)

        gorny = QHBoxLayout()

        combo = QComboBox()
        combo.setView(QListView())

        combo.addItem("Kolokwium", "Kolokwium")
        combo.addItem("Kartkowki", "Kartkowki")
        combo.addItem("Egzamin", "Egzamin")
        combo.addItem("Aktywnosc", "Aktywnosc")
        combo.addItem("Prezentacja", "Prezentacja")
        combo.addItem("Projekt", "Projekt")
        combo.addItem("Inne", "Inne")

        combo.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                color: #3D3450;
                border: 1.5px solid #D8C8F0;
                border-radius: 10px;
                padding: 8px 10px;
            }

            QComboBox::drop-down {
                border: none;
                background-color: #F5EEFF;
                width: 28px;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }

            QComboBox QListView {
                background-color: #FFFFFF;
                color: #3D3450;
                border: 1.5px solid #D8C8F0;
                selection-background-color: #EEE5FF;
                selection-color: #3D3450;
                outline: none;
            }
        """)

        pole_wlasne = QLineEdit()
        pole_wlasne.setPlaceholderText("Wpisz wlasna nazwe")
        pole_wlasne.setVisible(False)

        maks = QSpinBox()
        maks.setRange(1, 9999)
        maks.setValue(20)
        maks.setSuffix(" pkt")
        maks.setFixedWidth(110)

        btn_usun = QPushButton("Usun")
        btn_usun.setObjectName("btnWstecz")

        gorny.addWidget(combo)
        gorny.addWidget(maks)
        gorny.addWidget(btn_usun)

        wiersz_glowny.addLayout(gorny)
        wiersz_glowny.addWidget(pole_wlasne)

        dane_wiersza = {
            "widget": wiersz_widget,
            "combo": combo,
            "pole_wlasne": pole_wlasne,
            "maks": maks,
        }

        def po_zmianie_formy() -> None:
            typ = combo.currentData()
            pole_wlasne.setVisible(typ == "Inne")
            self._aktualizuj_numeracje_kolokwiow()

        def usun_wiersz() -> None:
            if len(self.wiersze_form_zaliczenia) <= 1:
                return

            if dane_wiersza in self.wiersze_form_zaliczenia:
                self.wiersze_form_zaliczenia.remove(dane_wiersza)

            wiersz_widget.deleteLater()
            self._aktualizuj_numeracje_kolokwiow()

        combo.currentIndexChanged.connect(po_zmianie_formy)
        btn_usun.clicked.connect(usun_wiersz)

        self.wiersze_form_zaliczenia.append(dane_wiersza)
        self.lista_warunkow_layout.addWidget(wiersz_widget)

        self._aktualizuj_numeracje_kolokwiow()

    def _aktualizuj_numeracje_kolokwiow(self) -> None:
        licznik = 0

        for wiersz in self.wiersze_form_zaliczenia:
            combo = wiersz["combo"]

            combo.blockSignals(True)

            if combo.itemData(0) == "Kolokwium":
                combo.setItemText(0, "Kolokwium")

            combo.blockSignals(False)

        for wiersz in self.wiersze_form_zaliczenia:
            combo = wiersz["combo"]

            if combo.currentData() == "Kolokwium":
                licznik += 1
                nazwa = f"Kolokwium {self._liczba_rzymska(licznik)}"

                combo.blockSignals(True)
                combo.setItemText(0, nazwa)
                combo.blockSignals(False)

    def _pobierz_elementy_zaliczenia(self) -> list:
        elementy = []
        licznik_kolokwiow = 0

        for wiersz in self.wiersze_form_zaliczenia:
            combo = wiersz["combo"]
            pole_wlasne = wiersz["pole_wlasne"]
            maks = wiersz["maks"]

            typ = combo.currentData()

            if typ == "Kolokwium":
                licznik_kolokwiow += 1
                nazwa = f"Kolokwium {self._liczba_rzymska(licznik_kolokwiow)}"

            elif typ == "Inne":
                nazwa = pole_wlasne.text().strip()

                if not nazwa:
                    continue

            else:
                nazwa = typ

            elementy.append({
                "nazwa": nazwa,
                "maks": maks.value(),
            })

        return elementy

    def _liczba_rzymska(self, liczba: int) -> str:
        rzymskie = [
            (1000, "M"),
            (900, "CM"),
            (500, "D"),
            (400, "CD"),
            (100, "C"),
            (90, "XC"),
            (50, "L"),
            (40, "XL"),
            (10, "X"),
            (9, "IX"),
            (5, "V"),
            (4, "IV"),
            (1, "I"),
        ]

        wynik = ""

        for wartosc, znak in rzymskie:
            while liczba >= wartosc:
                wynik += znak
                liczba -= wartosc

        return wynik

    def _zapisz_przedmiot(self) -> None:
        nazwa = self.pole_nazwa.text().strip()

        if not nazwa:
            return

        elementy = self._pobierz_elementy_zaliczenia()

        if not elementy:
            return

        suma_maks = sum(element["maks"] for element in elementy)

        self.dane_przedmiotow[nazwa] = {
            "prog": self.pole_prog.value(),
            "maks": suma_maks,
            "zdobyte": 0,
            "elementy": elementy,
        }

        self.pole_nazwa.clear()
        self.pole_prog.setValue(51)

        self._wyczysc_wiersze_form_zaliczenia()
        self._dodaj_wiersz_formy_zaliczenia()

        self._pokaz_glowna()

    def _wyczysc_wiersze_form_zaliczenia(self) -> None:
        for wiersz in self.wiersze_form_zaliczenia:
            wiersz["widget"].deleteLater()

        self.wiersze_form_zaliczenia.clear()
