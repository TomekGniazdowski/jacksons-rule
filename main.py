import funkcje

for i in range(1, 9):
    il_zadan, termin, czas = funkcje.odczyt_pliku(f'Input/JACK{i}.DAT')
    # w celu sprawdzenia danych
    # print('ilosc zadan:', il_zadan, 'termin dostepnosci:', termin, 'czas:', czas)
    wynik = funkcje.jackson_alghoritm(il_zadan, termin, czas)
    if funkcje.spr_wynik(f'Output/JACK{i}.DAT', wynik) == True:
        print(f'JACK{i} ->', wynik, '\u2713')
    else:
        print(f'JACK{i} ->', wynik, '\u2717')
