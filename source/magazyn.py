import json
from pathlib import Path
from PySide6.QtCore import QStandardPaths
from source.model import Przedmiot 

#MAGAZYN DANYCH
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

