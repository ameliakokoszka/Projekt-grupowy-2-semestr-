import pytest
from main import Przedmiot

@pytest.fixture
def analiza_matematyczna():
    progi = {"3.0": 50.0, "3.5": 60.0, "4.0": 70.0, "4.5": 80.0, "5.0": 90.0}
    elementy = [
        {"nazwa": "Kolo1", "maks": 50.0, "punkty": 0.0},
        {"nazwa": "Kolo2", "maks": 50.0, "punkty": 0.0}
    ]
    return Przedmiot("Analiza matematyczna", 50.0, elementy, progi)

def test_czy_dobrze_sumuje_max_punktow(analiza_matematyczna):
    """Sprawdza, czy program dobrze sumuje punkty z obu kolokwiów."""
    assert analiza_matematyczna.maks_punktow() == 100.0

@pytest.mark.parametrize("punkty, oczekiwany_status", [
    (0.0, False),
    (49.9, False),
    (50.0, True),
    (50.1, True),
    (100.0, True),
])
def test_czy_zalicza_przedmiot_dla_roznych_wynikow(analiza_matematyczna, punkty, oczekiwany_status):
    """Sprawdza, czy status zaliczenia zmienia się poprawnie w zależności od liczby punktów."""
    analiza_matematyczna.zdobyte_punkty = punkty
    assert analiza_matematyczna.czy_zaliczony() is oczekiwany_status

@pytest.mark.parametrize("punkty, oczekiwany_brak", [
    (0.0, 50.0),
    (25.0, 25.0),
    (49.9, 0.1),
    (50.0, 0.0),
    (75.0, 0.0),
])
def test_ile_punktow_brakuje_do_zaliczenia(analiza_matematyczna, punkty, oczekiwany_brak):
    """Sprawdza, czy poprawnie wylicza brakujące punkty do progu zaliczeniowego."""
    analiza_matematyczna.zdobyte_punkty = punkty
    assert analiza_matematyczna.ile_brakuje() == oczekiwany_brak

@pytest.mark.parametrize("punkty, oczekiwana_ocena", [
    (0.0, "2.0"),
    (49.9, "2.0"),
    (50.0, "3.0"),
    (59.9, "3.0"),
    (60.0, "3.5"),
    (69.9, "3.5"),
    (70.0, "4.0"),
    (79.9, "4.0"),
    (80.0, "4.5"),
    (89.9, "4.5"),
    (90.0, "5.0"),
    (100.0, "5.0"),
])
def test_wystawiania_ocen_dla_roznych_progow(analiza_matematyczna, punkty, oczekiwana_ocena):
    """Sprawdza, czy każda ocena od 2.0 do 5.0 jest prawidłowo przypisywana do punktów."""
    analiza_matematyczna.zdobyte_punkty = punkty
    assert analiza_matematyczna.aktualna_ocena() == oczekiwana_ocena

def test_ile_brakuje_do_troi_gdy_student_nie_zaliczyl(analiza_matematyczna):
    """Sprawdza podpowiedź o brakujących punktach do oceny 3.0, gdy przedmiot jest niezaliczony."""
    analiza_matematyczna.zdobyte_punkty = 40.0
    assert analiza_matematyczna.do_kolejnej_oceny() == "Brakuje 10.0 pkt do oceny 3.0"

def test_ile_brakuje_do_wyzszej_oceny_w_srodku_semestru(analiza_matematyczna):
    """Sprawdza informację o brakujących punktach do wyższej oceny, gdy student już zaliczył przedmiot."""
    analiza_matematyczna.zdobyte_punkty = 65.0
    assert analiza_matematyczna.do_kolejnej_oceny() == "Brakuje 5.0 pkt do oceny 4.0"

def test_komunikatu_gdy_student_ma_juz_maksa(analiza_matematyczna):
    """Sprawdza, czy program poprawnie reaguje, gdy student ma już najwyższą możliwą ocenę 5.0."""
    analiza_matematyczna.zdobyte_punkty = 95.0
    assert analiza_matematyczna.do_kolejnej_oceny() == "Osiągnięto ocenę 5.0"

def test_wygladu_calego_komunikatu_o_ocenie(analiza_matematyczna):
    """Sprawdza, czy dwulinijkowy tekst z podsumowaniem oceny i brakiem punktów generuje się poprawnie."""
    analiza_matematyczna.zdobyte_punkty = 55.0
    oczekiwany_tekst = "Masz ocenę: 3.0.\nBrakuje 5.0 pkt do oceny 3.5"
    assert analiza_matematyczna.komunikat_oceny() == oczekiwany_tekst

def test_zamiany_przedmiotu_na_slownik(analiza_matematyczna):
    """Sprawdza, czy dane przedmiotu poprawnie eksportują się do formatu słownika przed zapisem."""
    analiza_matematyczna.zdobyte_punkty = 75.0
    slownik = analiza_matematyczna.do_slownika()
    assert slownik["nazwa"] == "Analiza matematyczna"
    assert slownik["prog"] == 50.0
    assert slownik["zdobyte_punkty"] == 75.0
    assert len(slownik["elementy"]) == 2
    assert slownik["progi_ocen"]["5.0"] == 90.0

def test_odtworzenia_przedmiotu_ze_slownika(analiza_matematyczna):
    """Sprawdza, czy program potrafi bezbłędnie stworzyć obiekt przedmiotu na podstawie wczytanego słownika."""
    dane_testowe = {
        "nazwa": "Analiza matematyczna",
        "prog": 50.0,
        "elementy": [{"nazwa": "Kolo1", "maks": 50.0}, {"nazwa": "Kolo2", "maks": 50.0}],
        "progi_ocen": {"3.0": 50.0, "5.0": 90.0},
        "zdobyte_punkty": 85.5
    }
    nowy_przedmiot = Przedmiot.z_slownika(dane_testowe)
    assert nowy_przedmiot.nazwa == "Analiza matematyczna"
    assert nowy_przedmiot.zdobyte_punkty == 85.5
    assert nowy_przedmiot.prog == 50.0
    assert nowy_przedmiot.maks_punktow() == 100.0