import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QLineEdit, QSpinBox,
    QFrame, QProgressBar, QScrollArea, QComboBox, QListView
)

# STAŁE (kolory, ktore zostaly uzyte do stworzenia aplikacji)
KOLOR_TLA = "#FFFBF2"
KOLOR_TEKSTU = "#3D3450"
KOLOR_BIALY = "#FFFFFF"

# Stany (Zaliczone / Brakuje)
KOLOR_ZALICZONE = "#1A7A2A"
KOLOR_BRAKUJE = "#6A3D9E"

# Paski postępu
KOLOR_PASEK_TLO = "rgba(255,255,255,0.65)"
KOLOR_PASEK_ZALICZONE = "#88C98A"
KOLOR_PASEK_BRAKUJE = "#C9A8E0"

# Przyciski i interfejs
KOLOR_GLOWNY = "#C9A8E0"
KOLOR_GLOWNY_HOVER = "#B090D0"
KOLOR_PRZELICZ = "#F5B8D0"
KOLOR_PRZELICZ_TEKST = "#5A1A3A"
KOLOR_KRAWEDZI = "#D8C8F0"
KOLOR_TLO_HOVER = "#EEE5FF"
KOLOR_TLO_ZALICZONE = "#D4F0D4"

# Kolory pastelowe do kafelków z przedmiotami
KOLORY_KART = ["#FDEAF1", "#FFF8D6", "#EEE5FF", "#DFF7F0", "#FFE8D6"]

GLOWNY_STYL = f"""
    QMainWindow, QWidget#strona, QWidget#contentArea, QWidget#scrollKontener {{
        background-color: {KOLOR_TLA};
    }}
    QWidget {{
        font-family: 'Calibri', sans-serif; font-size: 15px; color: {KOLOR_TEKSTU};
    }}
    QPushButton {{
        font-weight: 700; border-radius: 10px; padding: 9px;
    }}
    QPushButton#btnDodaj {{ background-color: {KOLOR_GLOWNY}; color: {KOLOR_BIALY}; border: none; }}
    QPushButton#btnDodaj:hover {{ background-color: {KOLOR_GLOWNY_HOVER}; }}
    QPushButton#btnWstecz {{ background: transparent; color: {KOLOR_BRAKUJE}; border: none; }}
    QPushButton#btnWstecz:hover {{ background-color: {KOLOR_TLO_HOVER}; }}
    QPushButton#btnPrzelicz {{ background-color: {KOLOR_PRZELICZ}; color: {KOLOR_PRZELICZ_TEKST}; padding: 15px; border-radius: 14px; }}
    QLineEdit, QSpinBox, QComboBox {{
        border: 1.5px solid {KOLOR_KRAWEDZI}; border-radius: 10px; padding: 8px; background: {KOLOR_BIALY};
    }}
"""

# MODEL DANYCH 
class Przedmiot:
    """Klasa przechowująca dane i logikę obliczeń dla pojedynczego przedmiotu."""
    
    def __init__(self, nazwa: str, prog: int, elementy: list) -> None:
        """Tworzy nowy przedmiot z podaną nazwą, progiem i listą elementów."""
        self.nazwa = nazwa
        self.prog = prog
        self.elementy = elementy
        self.zdobyte_punkty = 0

    def maks_punktow(self) -> int:
        """Zwraca maksymalną możliwą liczbę punktów do zdobycia."""
        return sum(el["maks"] for el in self.elementy)

    def czy_zaliczony(self) -> bool:
        """Zwraca True, jeśli zdobyte punkty przekraczają lub równe są progowi."""
        return self.zdobyte_punkty >= self.prog

    def ile_brakuje(self) -> int:
        """Oblicza, ile punktów brakuje do zaliczenia."""
        if self.czy_zaliczony():
            return 0
        return self.prog - self.zdobyte_punkty

#WIDOK (Komponenty wizualne)

class KartaPrzedmiotu(QFrame):
    
    def __init__(self, przedmiot: Przedmiot, kolor: str, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.przedmiot = przedmiot
        self.btn_szczegoly = QPushButton("Otworz szczegoly  →")
        self._buduj_ui(kolor)

    def _buduj_ui(self, kolor: str) -> None:
        self.setStyleSheet(f"QFrame {{ background-color: {kolor}; border-radius: 18px; border: 1.5px solid rgba(0,0,0,0.06); }} QLabel {{ border: none; background: transparent; }}")
        u = QVBoxLayout(self)
        u.setContentsMargins(22, 18, 22, 18)
        
        nagl = QLabel(self.przedmiot.nazwa)
        nagl.setStyleSheet("font-size: 16px; font-weight: 700;")
        u.addWidget(nagl)

        pasek = QProgressBar()
        pasek.setMaximum(self.przedmiot.maks_punktow())
        pasek.setValue(self.przedmiot.zdobyte_punkty)
        pasek.setTextVisible(False)
        pasek.setFixedHeight(12)
        u.addWidget(pasek)

        wiersz = QHBoxLayout()
        info = QLabel(f"{self.przedmiot.zdobyte_punkty} / {self.przedmiot.maks_punktow()} pkt  •  Prog: {self.przedmiot.prog} pkt")
        wiersz.addWidget(info)
        wiersz.addStretch()

        st = QLabel()
        if self.przedmiot.czy_zaliczony():
            st.setText("Zaliczone!")
            st.setStyleSheet(f"color:{KOLOR_ZALICZONE}; font-weight:700; font-size:12px; background:transparent;")
        else:
            st.setText(f"Brakuje: {self.przedmiot.ile_brakuje()} pkt")
            st.setStyleSheet(f"color:{KOLOR_BRAKUJE}; font-weight:700; font-size:12px; background:transparent;")
        
        wiersz.addWidget(st)
        u.addLayout(wiersz)
        
        self.btn_szczegoly.setStyleSheet(f"background-color: {KOLOR_BIALY}; color: {KOLOR_BRAKUJE}; border: 1.5px solid {KOLOR_GLOWNY};")
        u.addWidget(self.btn_szczegoly)


# Kontroler (Główne okno)

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

# Budowanie Interfejsu
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

        for i, (nazwa, przedmiot) in enumerate(self.baza_przedmiotow.items()):
            karta = KartaPrzedmiotu(przedmiot, KOLORY_KART[i % len(KOLORY_KART)])
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
            kolor, tlo = KOLOR_ZALICZONE, KOLOR_TLO_ZALICZONE
        else:
            tekst = f"Brakuje Ci jeszcze {przedmiot.ile_brakuje()} pkt\nMasz {suma} pkt  •  Prog: {przedmiot.prog} pkt"
            kolor, tlo = KOLOR_BRAKUJE, KOLOR_TLO_HOVER

        self.etykieta_wyniku.setText(tekst)
        self.etykieta_wyniku.setStyleSheet(f"color: {kolor}; font-size: 15px; font-weight: 700; background-color: {tlo}; border-radius: 14px; padding: 18px;")

    def _wyczysc_layout(self, layout) -> None:
        """Narzędzie do czyszczenia układów z widżetów."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            elif item.layout(): self._wyczysc_layout(item.layout())

# Nawigacja
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
