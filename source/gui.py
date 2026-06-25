from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QLineEdit, QDoubleSpinBox,
    QFrame, QProgressBar, QScrollArea, QComboBox, QListView,
    QAbstractSpinBox
)

from src.model import Przedmiot
from src.magazyn import MagazynDanych

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
KOLOR_PASEK_BRAKUJE = "#E57373"

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
    QLineEdit, QDoubleSpinBox, QComboBox {{
        border: 1.5px solid {KOLOR_KRAWEDZI}; border-radius: 10px; padding: 8px; background: {KOLOR_BIALY};
    }}
    QDoubleSpinBox QLineEdit {{
        border: none; padding: 0; background: transparent;
    }}
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
        subcontrol-origin: border; width: 30px;
        background-color: {KOLOR_TLO_HOVER};
        border-left: 1.5px solid {KOLOR_KRAWEDZI};
    }}
    QDoubleSpinBox::up-button {{
        subcontrol-position: top right; border-top-right-radius: 9px;
        border-bottom: 1px solid {KOLOR_KRAWEDZI};
    }}
    QDoubleSpinBox::down-button {{
        subcontrol-position: bottom right; border-bottom-right-radius: 9px;
    }}
    QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
        background-color: {KOLOR_KRAWEDZI};
    }}
"""



class PolePunktow(QDoubleSpinBox):
    """Tworzy pole do wpisywania punktów."""
    
    def __init__(self, podpowiedz: str, minimum: float, maximum: float, parent: QWidget = None) -> None:
        """Ustawia zakres pola i tekst podpowiedzi."""
        super().__init__(parent)
        self.setRange(minimum, maximum)
        self.setDecimals(1)
        self.setSingleStep(1)
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.lineEdit().setPlaceholderText(podpowiedz)
        self.setValue(minimum)
        self.clear()

    def focusOutEvent(self, event) -> None:
        """Czyści puste pole po utracie zaznaczenia."""
        puste = not self.lineEdit().text().strip()
        super().focusOutEvent(event)
        if puste:
            self.setValue(self.minimum())
            self.clear()

    def jest_puste(self) -> bool:
        """Sprawdza, czy pole jest puste."""
        return not self.lineEdit().text().strip()


#WIDOK (Komponenty wizualne)
class KartaPrzedmiotu(QFrame):
    """Wyświetla najważniejsze informacje o przedmiocie."""
    
    def __init__(self, przedmiot: Przedmiot, kolor: str, parent: QWidget = None) -> None:
        """Tworzy kartę wybranego przedmiotu."""
        super().__init__(parent)
        self.przedmiot = przedmiot
        self.btn_szczegoly = QPushButton("Otwórz szczegóły  →")
        self.btn_usun = QPushButton("Usuń")
        self._buduj_ui(kolor)

    def _buduj_ui(self, kolor: str) -> None:
        """Buduje wygląd karty przedmiotu."""
        self.setStyleSheet(f"QFrame {{ background-color: {kolor}; border-radius: 18px; border: 1.5px solid rgba(0,0,0,0.06); }} QLabel {{ border: none; background: transparent; }}")
        u = QVBoxLayout(self)
        u.setContentsMargins(22, 18, 22, 18)
        
        naglowek = QHBoxLayout()
        nagl = QLabel(self.przedmiot.nazwa)
        nagl.setStyleSheet("font-size: 16px; font-weight: 700;")
        naglowek.addWidget(nagl)
        naglowek.addStretch()
        self.btn_usun.setFixedSize(60, 30)
        self.btn_usun.setStyleSheet(f"background-color: {KOLOR_BIALY}; color: {KOLOR_PASEK_BRAKUJE}; border: 1.5px solid {KOLOR_PASEK_BRAKUJE}; padding: 2px;")
        naglowek.addWidget(self.btn_usun)
        u.addLayout(naglowek)

        aktualna_ocena = QLabel(f"Aktualna ocena: {self.przedmiot.aktualna_ocena()}")
        aktualna_ocena.setAlignment(Qt.AlignCenter)
        aktualna_ocena.setStyleSheet("font-size: 13px; font-weight: 700; background: transparent;")
        u.addWidget(aktualna_ocena)

        pasek = QProgressBar()
        pasek.setMaximum(round(self.przedmiot.maks_punktow() * 10))
        pasek.setValue(round(self.przedmiot.zdobyte_punkty * 10))
        pasek.setTextVisible(False)
        pasek.setFixedHeight(12)
        kolor_paska = KOLOR_PASEK_ZALICZONE if self.przedmiot.czy_zaliczony() else KOLOR_PASEK_BRAKUJE
        pasek.setStyleSheet(f"QProgressBar {{ background-color: {KOLOR_PASEK_TLO}; border: none; border-radius: 6px; }} QProgressBar::chunk {{ background-color: {kolor_paska}; border-radius: 6px; }}")
        u.addWidget(pasek)
        kolejna_ocena = QLabel(self.przedmiot.do_kolejnej_oceny())
        kolejna_ocena.setAlignment(Qt.AlignCenter)
        kolejna_ocena.setStyleSheet("font-size: 13px; background: transparent;")
        u.addWidget(kolejna_ocena)

        wiersz = QHBoxLayout()
        info = QLabel(f"{self.przedmiot.zdobyte_punkty} / {self.przedmiot.maks_punktow()} pkt  •  Próg: {self.przedmiot.prog} pkt")
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
    """Obsługuje główne okno aplikacji."""
    
    def __init__(self) -> None:
        """Tworzy główne okno i wczytuje dane."""
        super().__init__()
        self.setWindowTitle("Kalkulator Punktów Studenckich")
        self.setGeometry(100, 100, 620, 720)
        self.setStyleSheet(GLOWNY_STYL)

        self.magazyn = MagazynDanych()
        self.baza_przedmiotow: dict[str, Przedmiot] = self.magazyn.wczytaj()
        self.wiersze_form_zaliczenia: list[dict] = []
        self.spinboxy: dict[str, PolePunktow] = {}

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

        if self.baza_przedmiotow:
            self._pokaz_glowna()
        else:
            self._pokaz_dodawanie()

# Budowanie Interfejsu
    def _buduj_glowna(self) -> None:
        """Buduje stronę z listą przedmiotów."""
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
        scroll.setObjectName("contentArea")
        scroll.setWidgetResizable(True)
        self.kontener_kart = QWidget()
        self.kontener_kart.setObjectName("scrollKontener")
        self.uklad_kart = QVBoxLayout(self.kontener_kart)
        self.uklad_kart.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.kontener_kart)
        uklad.addWidget(scroll)

    def _buduj_przedmiot(self) -> None:
        """Buduje stronę szczegółów przedmiotu."""
        uklad = QVBoxLayout(self.strona_przedmiotu)
        
        pasek = QHBoxLayout()
        btn_w = QPushButton("← Powrót")
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
        """Buduje formularz dodawania przedmiotu."""
        uklad = QVBoxLayout(self.strona_dodawania)
        
        pasek = QHBoxLayout()
        self.btn_w_dodawanie = QPushButton("← Powrót")
        self.btn_w_dodawanie.setObjectName("btnWstecz")
        self.btn_w_dodawanie.clicked.connect(self._powrot_z_dodawania)
        pasek.addWidget(self.btn_w_dodawanie)
        pasek.addStretch()
        self.tytul_dodawania = QLabel("Dodaj przedmiot")
        self.tytul_dodawania.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {KOLOR_BRAKUJE};")
        pasek.addWidget(self.tytul_dodawania)
        pasek.addStretch()
        uklad.addLayout(pasek)

        tu = QVBoxLayout()
        tu.addWidget(QLabel("Nazwa przedmiotu:"))
        self.pole_nazwa = QLineEdit()
        self.pole_nazwa.setMaxLength(100)
        self.pole_nazwa.setPlaceholderText("np. Analiza Matematyczna")
        tu.addWidget(self.pole_nazwa)

        self.pola_ocen = {}
        progi_layout = QHBoxLayout()
        for ocena, wartosc in [("3.0", 51), ("3.5", 61), ("4.0", 71), ("4.5", 81), ("5.0", 91)]:
            kolumna = QVBoxLayout()
            kolumna.addWidget(QLabel(f"Ocena {ocena}"))
            pole_oceny = PolePunktow(f"{wartosc:.1f}", 0, 150)
            self.pola_ocen[ocena] = pole_oceny
            pole_oceny.editingFinished.connect(self._aktualizuj_minima_ocen)
            kolumna.addWidget(pole_oceny)
            progi_layout.addLayout(kolumna)
        tu.addLayout(progi_layout)

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
    def _aktualizuj_minima_ocen(self) -> None:
        """Ustawia poprawne minimalne progi kolejnych ocen."""
        oceny = list(self.pola_ocen.keys())
        for i in range(1, len(oceny)):
            poprzednie = self.pola_ocen[oceny[i - 1]]
            biezace = self.pola_ocen[oceny[i]]
            puste = biezace.jest_puste()
            minimum = 0 if poprzednie.jest_puste() else min(150, round(poprzednie.value() + 0.1, 1))
            biezace.setMinimum(minimum)
            if puste:
                biezace.clear()

    def _odswiez_karty(self) -> None:
        """Odświeża karty przedmiotów na stronie głównej."""
        while self.uklad_kart.count():
            item = self.uklad_kart.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, (nazwa, przedmiot) in enumerate(self.baza_przedmiotow.items()):
            karta = KartaPrzedmiotu(przedmiot, KOLORY_KART[i % len(KOLORY_KART)])
            karta.btn_szczegoly.clicked.connect(lambda checked=False, n=nazwa: self._pokaz_przedmiot(n))
            karta.btn_usun.clicked.connect(lambda checked=False, n=nazwa: self._usun_przedmiot(n))
            self.uklad_kart.addWidget(karta)

    def _usun_przedmiot(self, nazwa: str) -> None:
        """Usuwa wybrany przedmiot."""
        del self.baza_przedmiotow[nazwa]
        self.magazyn.zapisz(self.baza_przedmiotow)
        self._odswiez_karty()
        
    def _dodaj_wiersz_formy_zaliczenia(self) -> None:
        """Dodaje nowe pole elementu zaliczenia."""
        wiersz_widget = QWidget()
        uklad = QHBoxLayout(wiersz_widget)
        
        pole = QLineEdit()
        pole.setPlaceholderText("Nazwa (np. Kolokwium 1)")
        maks = PolePunktow("20.0", 0.1, 150)
        
        uklad.addWidget(pole, 5)
        uklad.addWidget(maks, 1)

        self.wiersze_form_zaliczenia.append({"widget": wiersz_widget, "nazwa": pole, "maks": maks})
        self.lista_warunkow_layout.addWidget(wiersz_widget)

    def _zapisz_przedmiot(self) -> None:
        """Sprawdza formularz i zapisuje przedmiot."""
        nazwa = self.pole_nazwa.text().strip()
        if not nazwa: return
        if any(pole.jest_puste() for pole in self.pola_ocen.values()): return

        elementy = []
        for w in self.wiersze_form_zaliczenia:
            n = w["nazwa"].text().strip()
            if n:
                if w["maks"].jest_puste(): return
                elementy.append({"nazwa": n, "maks": w["maks"].value(), "punkty": 0.0})
        
        if not elementy: return

        progi_ocen = {ocena: pole.value() for ocena, pole in self.pola_ocen.items()}
        wartosci_progow = list(progi_ocen.values())
        if any(wartosci_progow[i] >= wartosci_progow[i + 1] for i in range(len(wartosci_progow) - 1)): return
        self.baza_przedmiotow[nazwa] = Przedmiot(nazwa, progi_ocen["3.0"], elementy, progi_ocen)
        self.magazyn.zapisz(self.baza_przedmiotow)

        self.pole_nazwa.clear()
        for pole in self.pola_ocen.values():
            pole.setMinimum(0)
            pole.setValue(pole.minimum())
            pole.clear()
        for w in self.wiersze_form_zaliczenia:
            w["widget"].deleteLater()
        self.wiersze_form_zaliczenia.clear()
        self._dodaj_wiersz_formy_zaliczenia()
        
        self._pokaz_glowna()

    def _zbuduj_pola_punktow(self, nazwa_przedmiotu: str) -> None:
        """Tworzy pola do wpisywania zdobytych punktów."""
        while self.uklad_punktow.count():
            item = self.uklad_punktow.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            elif item.layout(): self._wyczysc_layout(item.layout())

        self.spinboxy.clear()
        przedmiot = self.baza_przedmiotow[nazwa_przedmiotu]

        for el in przedmiot.elementy:
            wiersz = QHBoxLayout()
            wiersz.addWidget(QLabel(f"{el['nazwa']} (0-{el['maks']})"))
            spin = PolePunktow("0.0", 0, el["maks"])
            punkty = el.get("punkty", 0.0)
            if punkty > 0:
                spin.setValue(punkty)
            wiersz.addWidget(spin)
            self.spinboxy[el["nazwa"]] = spin
            self.uklad_punktow.addLayout(wiersz)

    def _przelicz(self) -> None:
        """Sumuje punkty i wyświetla wynik."""
        nazwa = self.etykieta_tytul.text()
        przedmiot = self.baza_przedmiotow[nazwa]
        
        suma = round(sum(0 if s.jest_puste() else s.value() for s in self.spinboxy.values()), 1)
        przedmiot.zdobyte_punkty = suma
        for el in przedmiot.elementy:
            spin = self.spinboxy.get(el["nazwa"])
            if spin is not None:
                el["punkty"] = 0.0 if spin.jest_puste() else spin.value()
        self.magazyn.zapisz(self.baza_przedmiotow)

        if przedmiot.czy_zaliczony():
            tekst = f"Zaliczone!\nMasz łącznie {suma} pkt\n{przedmiot.komunikat_oceny()}"
            kolor, tlo = KOLOR_ZALICZONE, KOLOR_TLO_ZALICZONE
        else:
            tekst = f"Niezaliczone!\nMasz łącznie {suma} pkt\n{przedmiot.komunikat_oceny()}"
            kolor, tlo = KOLOR_BRAKUJE, KOLOR_TLO_HOVER

        self.etykieta_wyniku.setText(tekst)
        self.etykieta_wyniku.setStyleSheet(f"color: {kolor}; font-size: 15px; font-weight: 700; background-color: {tlo}; border-radius: 14px; padding: 18px;")

    def _wyczysc_layout(self, layout) -> None:
        """Usuwa elementy z podanego układu."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            elif item.layout(): self._wyczysc_layout(item.layout())

# Nawigacja
    def _pokaz_glowna(self) -> None:
        """Pokazuje stronę główną."""
        self._odswiez_karty()
        self.stos.setCurrentIndex(0)

    def _pokaz_dodawanie(self) -> None:
        """Pokazuje formularz dodawania przedmiotu."""
        self.btn_w_dodawanie.setVisible(bool(self.baza_przedmiotow))
        self.stos.setCurrentIndex(2)

    def _powrot_z_dodawania(self) -> None:
        """Wraca z formularza do strony głównej."""
        if self.baza_przedmiotow: self._pokaz_glowna()

    def _pokaz_przedmiot(self, nazwa: str) -> None:
        """Pokazuje szczegóły wybranego przedmiotu."""
        self.etykieta_tytul.setText(nazwa)
        self.etykieta_wyniku.setText("")
        self.etykieta_wyniku.setStyleSheet("")
        self._zbuduj_pola_punktow(nazwa)
        self.stos.setCurrentIndex(1)

    def closeEvent(self, event) -> None:
        """Zapisuje dane przed zamknięciem aplikacji."""
        self.magazyn.zapisz(self.baza_przedmiotow)
        super().closeEvent(event)
