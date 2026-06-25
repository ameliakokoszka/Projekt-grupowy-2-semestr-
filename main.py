import sys
from PySide6.QtWidgets import QApplication

from src.gui import KalkulatorPunktow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    okno = KalkulatorPunktow()
    okno.show()
    
    sys.exit(app.exec())
