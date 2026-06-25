import pytest
from source.model import Przedmiot

PROGI_OCEN = {"3.0": 51.0, "3.5": 61.0, "4.0": 71.0, "4.5": 81.0, "5.0": 91.0}

ELEMENTY = [
    {"nazwa": "Kolokwium", "maks": 50.0, "punkty": 0.0},
    {"nazwa": "Projekt", "maks": 50.0, "punkty": 0.0}
]

def test_maks_punktow():
    """Sprawdza, czy poprawnie sumuje maksymalną liczbę punktów."""
    przedmiot = Przedmiot("Matematyka", 51.0, ELEMENTY, PROGI_OCEN)
    assert przedmiot.maks_punktow() == 100.0


def test_czy_zaliczony_gdy_ponizej_progu():
    """Sprawdza, czy przedmiot jest niezaliczony, gdy brakuje punktów."""
    przedmiot = Przedmiot("Matematyka", 51.0, ELEMENTY, PROGI_OCEN)
    przedmiot.zdobyte_punkty = 45.0
    assert przedmiot.czy_zaliczony() is False
    assert przedmiot.ile_brakuje() == 6.0


def test_czy_zaliczony_gdy_rowno_z_progiem():
    """Sprawdza warunek brzegowy: dokładnie tyle punktów ile wynosi próg."""
    przedmiot = Przedmiot("Matematyka", 51.0, ELEMENTY, PROGI_OCEN)
    przedmiot.zdobyte_punkty = 51.0
    assert przedmiot.czy_zaliczony() is True
    assert przedmiot.ile_brakuje() == 0.0


@pytest.mark.parametrize("zdobyte, oczekiwana_ocena", [
    (40.0, "2.0"),
    (51.0, "3.0"),
    (55.0, "3.0"),
    (61.0, "3.5"),
    (95.0, "5.0"),
])
def test_aktualna_ocena(zdobyte, oczekiwana_ocena):
    """Test parametryzowany - sprawdza wiele różnych wyników punktowych na raz."""
    przedmiot = Przedmiot("Matematyka", 51.0, ELEMENTY, PROGI_OCEN)
    przedmiot.zdobyte_punkty = zdobyte
    
    assert przedmiot.aktualna_ocena() == oczekiwana_ocena
