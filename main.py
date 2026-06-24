"""Aplikacja do obliczania punktów i ocen z przedmiotów."""
import sys
import json
from pathlib import Path
from PySide6.QtCore import Qt, QStandardPaths
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QLineEdit, QDoubleSpinBox,
    QFrame, QProgressBar, QScrollArea, QComboBox, QListView,
    QAbstractSpinBox
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

# MODEL DANYCH 
class Przedmiot:
    """Przechowuje dane jednego przedmiotu."""
    
    def __init__(self, nazwa: str, prog: float, elementy: list, progi_ocen: dict) -> None:
        """Tworzy nowy przedmiot z podanymi danymi."""
        self.nazwa = nazwa
        self.prog = prog
        self.elementy = elementy
        self.progi_ocen = progi_ocen
        self.zdobyte_punkty = 0.0

    def maks_punktow(self) -> float:
        """Oblicza maksymalną liczbę punktów."""
        return round(sum(el["maks"] for el in self.elementy), 1)

    def czy_zaliczony(self) -> bool:
        """Sprawdza, czy przedmiot jest zaliczony."""
        return self.zdobyte_punkty >= self.prog

    def ile_brakuje(self) -> float:
        """Oblicza liczbę punktów brakujących do zaliczenia."""
        if self.czy_zaliczony():
            return 0
        return round(self.prog - self.zdobyte_punkty, 1)

    def aktualna_ocena(self) -> str:
        """Wyznacza aktualną ocenę na podstawie punktów."""
        aktualna = "2.0"
        for ocena in self.progi_ocen.keys():
            if self.zdobyte_punkty >= self.progi_ocen[ocena]:
                aktualna = ocena
        return aktualna

    def do_kolejnej_oceny(self) -> str:
        """Podaje, ile punktów brakuje do kolejnej oceny."""
        for ocena in self.progi_ocen.keys():
            if self.zdobyte_punkty < self.progi_ocen[ocena]:
                return f"Brakuje {round(self.progi_ocen[ocena] - self.zdobyte_punkty, 1)} pkt do oceny {ocena}"
        return "Osiągnięto ocenę 5.0"

    def komunikat_oceny(self) -> str:
        """Tworzy komunikat o aktualnej i kolejnej ocenie."""
        ocena = self.aktualna_ocena()
        if ocena == "5.0":
            return f"Masz ocenę: {ocena}"
        return f"Masz ocenę: {ocena}.\n{self.do_kolejnej_oceny()}"

    def do_slownika(self) -> dict:
        """Zamienia dane przedmiotu na słownik."""
        return {
            "nazwa": self.nazwa,
            "prog": self.prog,
            "elementy": self.elementy,
            "progi_ocen": self.progi_ocen,
            "zdobyte_punkty": self.zdobyte_punkty,
        }

    @classmethod
    def z_slownika(cls, dane: dict) -> "Przedmiot":
        """Tworzy przedmiot z danych zapisanych w słowniku."""
        przedmiot = cls(dane["nazwa"], dane["prog"], dane["elementy"], dane["progi_ocen"])
        przedmiot.zdobyte_punkty = dane.get("zdobyte_punkty", 0.0)
        return przedmiot


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

class MagazynDanych:
    """Zapisuje i wczytuje dane z pliku JSON."""

    def __init__(self, nazwa_pliku: str = "dane.json") -> None:
        """Ustawia miejsce zapisu danych aplikacji."""
        katalog = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        Path(katalog).mkdir(parents=True, exist_ok=True)
        self.sciezka = Path(katalog) / nazwa_pliku

    def zapisz(self, baza_przedmiotow: dict) -> None:
        """Zapisuje przedmioty do pliku JSON."""
        dane = [przedmiot.do_slownika() for przedmiot in baza_przedmiotow.values()]
        try:
            with open(self.sciezka, "w", encoding="utf-8") as plik:
                json.dump(dane, plik, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def wczytaj(self) -> dict:
        """Wczytuje przedmioty z pliku JSON."""
        if not self.sciezka.exists():
            return {}
        try:
            with open(self.sciezka, "r", encoding="utf-8") as plik:
                dane = json.load(plik)
        except (OSError, json.JSONDecodeError):
            return {}

        baza = {}
        for wpis in dane:
            try:
                przedmiot = Przedmiot.z_slownika(wpis)
                baza[przedmiot.nazwa] = przedmiot
            except (KeyError, TypeError, ValueError):
                continue
        return baza


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
