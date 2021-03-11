def konwersja_str_int(s):
    # rzutowanie str->int wszystkich elementow w liscie
    for i in range(len(s)):
        s[i] = int(s[i])
    return s


def odczyt_pliku(nazwa_pliku):
    # otwarcie pliku w trybie do odczytu
    f = open(nazwa_pliku, 'r')
    # zmienne - termin dostepnosci, czas, ilosc zadan oraz licznik pomocniczy
    r = []
    p = []
    n = 0
    c = 0
    # odczyt linii -> kazda kolejna linia jest umieszczana jako osobny element listy
    lin = f.readlines()
    # rstrip('\n') - pomija znak konca linii, split(' ') pomija spacje i dzieli elementy na pojedyncze elementy
    for l in lin:
        if c == 0:
            n = l.rstrip('\n')
        else:
            s = l.rstrip('\n').split(' ')
            r.append(s[0])
            p.append(s[1])
        c += 1
    # zamkniecie pliku na koniec
    f.close()
    # zwrocenie
    return int(n), konwersja_str_int(r), konwersja_str_int(p)


def jackson_alghoritm(il_zadan, termin, czas):
    # sortujemy względem terminu i analogicznie zamieniamy miejscami czas
    for i in range(0, il_zadan):
        for j in range(1, il_zadan):
            if termin[j - 1] > termin[j]:
                termin[j - 1], termin[j] = termin[j], termin[j - 1]  # zamiana termin[j-1] z termin[j]
                czas[j - 1], czas[j] = czas[j], czas[j - 1]  # analogiczna zamiana jak wyzej

    # dane wyjściowe
    output = []

    for i in range(0, il_zadan):
        # dla pierwszego wykonania porównujemy z zerem aby uniknąć przekroczenia tablicy -> (output[-1])
        if i == 0:
            output.append(max(termin[i], 0) + czas[i])
        # dalej normalnie porównujemy z output[i-1]
        else:
            output.append(max(termin[i], output[i - 1]) + czas[i])

    # zwrocenie wyniku
    return output.pop()


def spr_wynik(nazwa_pliku, rzeczywisty_wynik):
    f = open(nazwa_pliku, 'r')
    poprawny_wynik = konwersja_str_int(f.readlines())[0]
    f.close()
    if poprawny_wynik == rzeczywisty_wynik:
        return True
    else:
        return False
