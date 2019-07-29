
# Metody do sprawdzenia w kazdym tescie:
# self._get_chance_to_get_sick()

# Scenario 1
# Brak chorob
# Jeden mieszkaniec, dom pollution=50, praca pollution=50
# Nastepna tura
# Nowa choroba powstaje
# Zaklad pracy w ktorej pracuje osoba z choroba ma mniejsza produktywnosc

# Scenario 2
# Klinika, lekarz profesjonalista 100
# Jedna osoba, z choroba
# Zaklad pracy w ktorej pracuje osoba z choroba ma mniejsza produktywnosc
# Natepna tura
# Brak chorob

# Scenario 3
# Osoba, ze smiertelna choroba, fatal_counter=10
# Nastepna tura
# Osoba umiera
# Zostaja usuniete wszystkie zawody, edukacja, choroby, miejsce pracy sie zwalnia,
# miejsce w domu sie zwalnia, pieniadze sa przekazane rodzinie

# Scenario 4
# Osoba, z choroba, fatal_counter=0
# Zaklad pracy w ktorej pracuje osoba z choroba ma mniejsza produktywnosc
# Tura do przodu
# Osoba zyje, fatal_counter choroby == 1
# Zaklad pracy w ktorej pracuje osoba z choroba ma mniejsza produktywnosc

# Scenario 5
# Osoba z choroba, fatal_counter=20
# Osoba z rodziny, dziecko z rodziny
# Tura do przodu
# Osoba umiera
# Małożonek i dziecko dostają osoba.cash / na ilosc czlonkow rodziny