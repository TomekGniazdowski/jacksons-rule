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
