import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QLineEdit, QSpinBox,
    QFrame, QProgressBar, QScrollArea, QComboBox, QListView
)


###Glowne okno
class KalkulatorPunktow(QMainWindow):
    """Główne okno zarządzające nawigacją i formularzami aplikacji."""
    
    def __init__(self) -> None:
        """Inicjalizuje główne okno i ustawia strukturę stron."""
        super().__init__()
        self.setWindowTitle("Kalkulator Punktow Studenckich")
        self.setGeometry(100, 100, 620, 720)
        self.setStyleSheet(GLOWNY_STYL)

        self.baza_przedmiotow: dict[str, Przedmiot] = {}
        self.wiersze_form_zaliczenia: list[dict] = []
        self.spinboxy: dict[str, QSpinBox] = {}

        self.stos = QStackedWidget()
        self.setCentralWidget(self.stos)

        self.strona_glowna = QWidget()
        self.strona_glowna.setObjectName("strona")
        self.strona_przedmiotu = QWidget()
        self.strona_przedmiotu.setObjectName("strona")
        self.strona_dodawania = QWidget()
        self.strona_dodawania.setObjectName("strona")

        self.stos.addWidget(self.strona_glowna)
        self.stos.addWidget(self.strona_przedmiotu)
        self.stos.addWidget(self.strona_dodawania)

        self._buduj_glowna()
        self._buduj_przedmiot()
        self._buduj_dodawanie()

        self._pokaz_dodawanie()

    ###
    # Budowanie Innterfejsu
    def _buduj_glowna(self) -> None:
        """Buduje widok strony głównej z listą przedmiotów."""
        uklad = QVBoxLayout(self.strona_glowna)
        uklad.setContentsMargins(0, 0, 0, 0)

        pasek = QHBoxLayout()
        pasek.setContentsMargins(24, 18, 24, 18)
        tytul = QLabel("Moje przedmioty")
        tytul.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {KOLOR_BRAKUJE};")
        pasek.addWidget(tytul)
        pasek.addStretch()
        
        btn = QPushButton("+ Dodaj przedmiot")
        btn.setObjectName("btnDodaj")
        btn.clicked.connect(self._pokaz_dodawanie)
        pasek.addWidget(btn)
        uklad.addLayout(pasek)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.kontener_kart = QWidget()
        self.uklad_kart = QVBoxLayout(self.kontener_kart)
        self.uklad_kart.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.kontener_kart)
        uklad.addWidget(scroll)

    def _buduj_przedmiot(self) -> None:
        """Buduje widok detali przedmiotu i przeliczania punktów."""
        uklad = QVBoxLayout(self.strona_przedmiotu)
        
        pasek = QHBoxLayout()
        btn_w = QPushButton("← Powrot")
        btn_w.setObjectName("btnWstecz")
        btn_w.clicked.connect(self._pokaz_glowna)
        pasek.addWidget(btn_w)
        pasek.addStretch()
        self.etykieta_tytul = QLabel("")
        self.etykieta_tytul.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {KOLOR_BRAKUJE};")
        pasek.addWidget(self.etykieta_tytul)
        pasek.addStretch()
        uklad.addLayout(pasek)

        tu = QVBoxLayout()
        self.uklad_punktow = QVBoxLayout()
        tu.addLayout(self.uklad_punktow)

        btn_przelicz = QPushButton("Przelicz punkty")
        btn_przelicz.setObjectName("btnPrzelicz")
        btn_przelicz.clicked.connect(self._przelicz)
        tu.addWidget(btn_przelicz)

        self.etykieta_wyniku = QLabel("")
        self.etykieta_wyniku.setAlignment(Qt.AlignCenter)
        self.etykieta_wyniku.setMinimumHeight(80)
        tu.addWidget(self.etykieta_wyniku)
        tu.addStretch()
        
        uklad.addLayout(tu)

    def _buduj_dodawanie(self) -> None:
        """Buduje widok formularza dodawania nowego przedmiotu."""
        uklad = QVBoxLayout(self.strona_dodawania)
        
        pasek = QHBoxLayout()
        btn_w = QPushButton("← Powrot")
        btn_w.setObjectName("btnWstecz")
        btn_w.clicked.connect(self._powrot_z_dodawania)
        pasek.addWidget(btn_w)
        pasek.addStretch()
        self.tytul_dodawania = QLabel("Dodaj przedmiot")
        self.tytul_dodawania.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {KOLOR_BRAKUJE};")
        pasek.addWidget(self.tytul_dodawania)
        pasek.addStretch()
        uklad.addLayout(pasek)

        tu = QVBoxLayout()
        tu.addWidget(QLabel("Nazwa przedmiotu:"))
        self.pole_nazwa = QLineEdit()
        tu.addWidget(self.pole_nazwa)

        tu.addWidget(QLabel("Prog zaliczenia:"))
        self.pole_prog = QSpinBox()
        self.pole_prog.setRange(0, 9999)
        self.pole_prog.setValue(51)
        tu.addWidget(self.pole_prog)

        self.lista_warunkow_layout = QVBoxLayout()
        tu.addLayout(self.lista_warunkow_layout)

        btn_dodaj_warunek = QPushButton("+ Dodaj element zaliczenia")
        btn_dodaj_warunek.clicked.connect(self._dodaj_wiersz_formy_zaliczenia)
        tu.addWidget(btn_dodaj_warunek)

        btn_zap = QPushButton("Zapisz przedmiot")
        btn_zap.setObjectName("btnPrzelicz")
        btn_zap.clicked.connect(self._zapisz_przedmiot)
        tu.addWidget(btn_zap)
        tu.addStretch()

        uklad.addLayout(tu)
        self._dodaj_wiersz_formy_zaliczenia()

    # Logika Aplikacji
    def _odswiez_karty(self) -> None:
        """Odświeża listę kart przedmiotów na stronie głównej."""
        while self.uklad_kart.count():
            item = self.uklad_kart.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        kolory = ["#FDEAF1", "#FFF8D6", "#EEE5FF", "#DFF7F0", "#FFE8D6"]
        for i, (nazwa, przedmiot) in enumerate(self.baza_przedmiotow.items()):
            karta = KartaPrzedmiotu(przedmiot, kolory[i % len(kolory)])
            karta.btn_szczegoly.clicked.connect(lambda checked=False, n=nazwa: self._pokaz_przedmiot(n))
            self.uklad_kart.addWidget(karta)

    def _dodaj_wiersz_formy_zaliczenia(self) -> None:
        """Dodaje nowy wiersz formularza elementu oceniania."""
        wiersz_widget = QWidget()
        uklad = QHBoxLayout(wiersz_widget)
        
        pole = QLineEdit()
        pole.setPlaceholderText("Nazwa (np. Kolokwium 1)")
        maks = QSpinBox()
        maks.setRange(1, 9999)
        maks.setValue(20)
        
        uklad.addWidget(pole)
        uklad.addWidget(maks)

        self.wiersze_form_zaliczenia.append({"widget": wiersz_widget, "nazwa": pole, "maks": maks})
        self.lista_warunkow_layout.addWidget(wiersz_widget)

    def _zapisz_przedmiot(self) -> None:
        """Zapisuje nowy przedmiot do bazy danych z formularza."""
        nazwa = self.pole_nazwa.text().strip()
        if not nazwa: return

        elementy = []
        for w in self.wiersze_form_zaliczenia:
            n = w["nazwa"].text().strip()
            if n:
                elementy.append({"nazwa": n, "maks": w["maks"].value()})
        
        if not elementy: return

        self.baza_przedmiotow[nazwa] = Przedmiot(nazwa, self.pole_prog.value(), elementy)

        self.pole_nazwa.clear()
        for w in self.wiersze_form_zaliczenia:
            w["widget"].deleteLater()
        self.wiersze_form_zaliczenia.clear()
        self._dodaj_wiersz_formy_zaliczenia()
        
        self._pokaz_glowna()

    def _zbuduj_pola_punktow(self, nazwa_przedmiotu: str) -> None:
        """Buduje dynamiczne pola do wpisywania zdobytych punktów."""
        while self.uklad_punktow.count():
            item = self.uklad_punktow.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            elif item.layout(): self._wyczysc_layout(item.layout())

        self.spinboxy.clear()
        przedmiot = self.baza_przedmiotow[nazwa_przedmiotu]

        for el in przedmiot.elementy:
            wiersz = QHBoxLayout()
            wiersz.addWidget(QLabel(f"{el['nazwa']} (0-{el['maks']})"))
            spin = QSpinBox()
            spin.setRange(0, el["maks"])
            wiersz.addWidget(spin)
            self.spinboxy[el["nazwa"]] = spin
            self.uklad_punktow.addLayout(wiersz)

    def _przelicz(self) -> None:
        """Przelicza punkty na podstawie wpisanych danych i aktualizuje obiekt."""
        nazwa = self.etykieta_tytul.text()
        przedmiot = self.baza_przedmiotow[nazwa]
        
        suma = sum(s.value() for s in self.spinboxy.values())
        przedmiot.zdobyte_punkty = suma

        if przedmiot.czy_zaliczony():
            tekst = f"Zaliczone!\nMasz lacznie {suma} pkt"
            kolor, tlo = KOLOR_ZALICZONE, "#D4F0D4"
        else:
            tekst = f"Brakuje Ci jeszcze {przedmiot.ile_brakuje()} pkt\nMasz {suma} pkt  •  Prog: {przedmiot.prog} pkt"
            kolor, tlo = KOLOR_BRAKUJE, "#EEE5FF"

        self.etykieta_wyniku.setText(tekst)
        self.etykieta_wyniku.setStyleSheet(f"color: {kolor}; font-size: 15px; font-weight: 700; background-color: {tlo}; border-radius: 14px; padding: 18px;")

    def _wyczysc_layout(self, layout) -> None:
        """Narzędzie do czyszczenia układów z widżetów."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            elif item.layout(): self._wyczysc_layout(item.layout())
###


    # --- NAWIGACJA ---
    def _pokaz_glowna(self) -> None:
        """Przełącza widok na stronę główną."""
        self._odswiez_karty()
        self.stos.setCurrentIndex(0)

    def _pokaz_dodawanie(self) -> None:
        """Przełącza widok na stronę dodawania."""
        self.stos.setCurrentIndex(2)

    def _powrot_z_dodawania(self) -> None:
        """Powraca ze strony dodawania, jeśli są już przedmioty."""
        if self.baza_przedmiotow: self._pokaz_glowna()

    def _pokaz_przedmiot(self, nazwa: str) -> None:
        """Otwiera stronę detali konkretnego przedmiotu."""
        self.etykieta_tytul.setText(nazwa)
        self.etykieta_wyniku.setText("")
        self.etykieta_wyniku.setStyleSheet("")
        self._zbuduj_pola_punktow(nazwa)
        self.stos.setCurrentIndex(1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    okno = KalkulatorPunktow()
    okno.show()
    sys.exit(app.exec())
