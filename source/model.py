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

