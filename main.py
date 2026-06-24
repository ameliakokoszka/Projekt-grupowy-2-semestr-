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

