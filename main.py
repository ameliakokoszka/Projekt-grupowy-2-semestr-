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
