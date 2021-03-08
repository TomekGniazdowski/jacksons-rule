# Tomasz Gniazdowski i Michał Łopatka
import gensim
from gensim.test.utils import datapath
from gensim.models import KeyedVectors
from google.colab import drive
from google.colab import drive
from google.colab import files
from difflib import SequenceMatcher
import unicodedata
import re
import string
import copy
import pandas as pd
import numpy as np
import io
import roman
from IPython.display import clear_output

# fuzzywuzzy
import difflib
from fuzzywuzzy import fuzz

from collections import OrderedDict

# Pobranie exceli
data_ofic = files.upload()
data_jsos = files.upload()

# odczyt exceli danych wzorcowych i danych z jsosa
of_exl = pd.read_excel(io.BytesIO(data_ofic['data_of.xlsx']), index_col=None, header=0,
                       usecols="A, N, D, E, P, Q, S, E")
of_exl["Nazwa oryginalna"] = of_exl["Nazwa"]
js_exl = pd.read_excel(io.BytesIO(data_jsos['data_js.xlsx']), index_col=None, header=0, usecols="A:D")

js_exl = js_exl.dropna(thresh=2)
js_kopia = js_exl.copy()
js_exl

of_exl = of_exl.dropna(thresh=5)
of_kopia = of_exl.copy()
of_exl.head(5)

# pozostawienie szkół ponadgimnazjalnych

of_exl = of_exl.dropna(thresh=5)
of_exl['Numer RSPO'] = of_exl['Numer RSPO'].fillna(0.0).astype(float)
of_exl['Numer RSPO'] = of_exl['Numer RSPO'].astype(int)

of_exl.head(5)


# okrelenie stopnia podobienstwa dwoch stringow
def w_similar(a, b):
    if a != None and b != None:
        return SequenceMatcher(None, a, b).ratio()
    else:
        return 0


# normalizowanie charow
# polskie znaki -> ASCII
def normalize_char(c):
    if type(c) == str:
        c = c.lower()
        pol = ['ą', 'ć', 'ę', 'ł', 'ń', 'ó', 'ś', 'ź', 'ż']
        ASCII = ['a', 'c', 'e', 'l', 'n', 'o', 's', 'z', 'z']
        for i in range(len(pol)):
            if c == pol[i]:
                c = ASCII[i]
        return c


def normalize_string(s):
    if type(s) == str:
        rs = ''
        # usuwanie polsich znakow
        for i in s:
            rs += normalize_char(i)
        # usuwanie zbednych spacji
        rs = ' '.join(rs.split())
        return rs


str_base = ['os.', 'ul.', 'al.', 'pl.' 'os', 'ul', 'al', 'pl', 'ulica', 'plac', 'aleja', 'osiedle']


def delstr(s):
    for b in str_base:
        if s == b:
            s = ''
            return s
    return s


# usuniecie 'ul.', 'pl.', 'ul', 'pl' itp. z nazw ulic
def del_ul(s):
    re = ""
    if type(s) == str:
        s = s.split()
        for e in s:
            re += delstr(e) + ' '
    return re


# obrobka danych wzorcowych
of_exl['Typ'] = of_exl['Typ'].apply(normalize_string)
of_exl['Miejscowość'] = of_exl['Miejscowość'].apply(normalize_string)
of_exl['Nazwa'] = of_exl['Nazwa'].apply(normalize_string)
of_exl['Ulica'] = of_exl['Ulica'].apply(normalize_string)
of_exl['Ulica'] = of_exl['Ulica'].apply(del_ul)

of_exl.head(5)


# szablon do znajdowania kodu pocztowego
def post_code(s):
    post_code = re.compile(r'\d\d-\d\d\d')
    pc_patt = post_code.search(s)
    if pc_patt != None:
        return pc_patt.group()
    else:
        return None


# szblon do znajdowania numeru budynku
def num_find(s):
    n = re.findall(r'\d+\w', s)
    if n != []:
        return n
    else:
        n = re.findall(r'\d+', s)
    return n


# przetworzenie wektora numeru budynku, normalizowanie numoerow
def num_stan(s):
    if len(s) == 1:
        return s[0]
    # 20 i 4 -> 20/4
    elif len(s) > 1:
        return s[0] + '/' + s[1]


# szblon do znajdowania numeru w nazwie ulicy
def num_street_find(s):
    s = s.replace(' ', '')

    n = re.match(r'(.*)-go', s)
    if n != None:
        return n.group(1), str(-1)

    n = re.match(r'(.*)-ego', s)
    if n != None:
        return n.group(1), str(-2)

    else:
        return '', str(0)


# czyszczenie stringow ze zbednych znakow
def ad_clean(s):
    getVals = list([val for val in s if val.isalpha() or val.isnumeric() or val == ' '])
    result = "".join(getVals)
    return result


# ujednolicenie liczb w nazwach szkół na rzymskie
def isNotBlank(myString):
    return bool(myString and myString.strip())


def school_name(s):
    if isNotBlank(s) == True:
        s = normalize_string(s)
        n = s.split()
        r = []
        for j in range(len(n) + 1):
            r.append(False)
        for i in range(len(n)):
            r[i] = n[i].isnumeric()
            if r[i] == True:
                n[i] = int(n[i])
                if n[i] < 5000:
                    n[i] = roman.toRoman(n[i])
                    n[i] = n[i].lower()
                n[i] = str(n[i])
            napis = ' '.join(n)
        return napis
    else:
        return s


def w_out(s):
    n = s.split()
    for i in range(len(n)):
        if n[i] == "w" or n[i] == 'we':
            return ' '.join(n[:i])
            break
    return ' '.join(n)


def patron_out(s):
    n = s.split()
    for i in range(len(n)):
        if n[i] == "im." or n[i] == "im" or n[i] == "imienia":
            return ' '.join(n[:i])
            break
    return ' '.join(n)


def patron_in(s):
    s = s.replace('.', ' ')
    n = s.split()
    flaga = 0
    for i in range(len(n)):
        if n[i] == "im." or n[i] == "im" or n[i] == "imienia":
            return ' '.join(n[i + 1:])
            flaga = 1
            break
    if flaga == 1:
        return ' '.join(n)
    else:
        return ''


def lo_full(s):
    n = s.split()
    for i in range(len(n)):
        if n[i] == 'lo':
            n[i] = 'liceum ogolnokszatlcace'
            return ' '.join(n)
            break
    return ' '.join(n)


# wyrzucenie nr
def nr_out(s):
    s = s.replace('nr ', ' ')
    s = s.replace('nr. ', ' ')
    s = s.replace('numer ', ' ')
    return s


def dash_out(s):
    s = s.replace('-', ' ').split(' ', 1)[0]
    return s


of_exl['Nazwa'] = of_exl['Nazwa'].apply(w_out)
of_exl["Patron"] = of_exl["Nazwa"]
of_exl['Nazwa'] = of_exl['Nazwa'].apply(patron_out)
of_exl['Patron'] = of_exl['Patron'].apply(patron_in)
of_exl['Nazwa'] = of_exl['Nazwa'].apply(nr_out)
of_exl['Nazwa'] = of_exl['Nazwa'].apply(school_name)
of_exl.head(20)

js_exl['SZKOLA_SR'] = js_exl['SZKOLA_SR'].apply(normalize_string)
js_exl['LOKALIZACJA_SZKOLY_SR'] = js_exl['LOKALIZACJA_SZKOLY_SR'].apply(normalize_string)
js_exl['ADRES_SR'] = js_exl['ADRES_SR'].apply(normalize_string)
js_exl['ADRES_SR'] = js_exl['ADRES_SR'].apply(del_ul)
js_exl['SZKOLA_SR'] = js_exl['SZKOLA_SR'].apply(w_out)
js_exl["PATRON"] = js_exl['SZKOLA_SR']
js_exl['SZKOLA_SR'] = js_exl['SZKOLA_SR'].apply(patron_out)
js_exl['PATRON'] = js_exl['PATRON'].apply(patron_in)
js_exl['SZKOLA_SR'] = js_exl['SZKOLA_SR'].apply(nr_out)
js_exl['SZKOLA_SR'] = js_exl['SZKOLA_SR'].apply(school_name)
js_exl['SZKOLA_SR'] = js_exl['SZKOLA_SR'].apply(lo_full)
js_exl['LOKALIZACJA_SZKOLY_SR'] = js_exl['LOKALIZACJA_SZKOLY_SR'].apply(dash_out)

js_exl.head(20)


# szblon do znajdowania typu szkoly
def school_type_find(s):
    s = s.replace(' ', '')

    t = s.find('liceum')
    if t != -1:
        return 'liceum ogolnoksztalcace'

    t = s.find('lo')
    if t != -1:
        return 'liceum ogolnoksztalcace'

    t = s.find('technikum')
    if t != -1:
        return 'technikum'

    t = s.find('zespolszkol')
    if t != -1:
        return 'zespol szkol i placowek oswiatowych'

    return None


# pobieranie okreslonych wartosci skladowych adresu
def find_adress(s_ci, s_ad, school):
    # adresy
    adress = s_ad
    # miasto
    city = s_ci

    # usuniecie ulicy, miasta
    adress = del_ul(normalize_string(adress))
    city = normalize_string(city)
    school_type = school_type_find(normalize_string(school))
    adress = adress.replace(city, '')

    # znajdowanie kodu pocztowego, usuniecie go
    postcode = post_code(adress)
    adress = adress.replace(str(postcode), '')

    # sprawdzenie, czy w nazwie ulicy nie ma liczby (np. 1-ego maja)
    num_street_name, flag = num_street_find(adress)

    if int(flag) == 0:
        pass

    # -go
    if int(flag) == -1:
        adress = adress.replace(num_street_name, '')
        adress = adress.replace('-go', '')

    # -ego
    if int(flag) == -2:
        adress = adress.replace(num_street_name, '')
        adress = adress.replace('-ego', '')

    # znajdowanie numeru budynku
    num_w = num_find(adress)
    for n in num_w:
        adress = adress.replace(n, '')

    # przetworzenie wektora num
    if num_w != None:
        num = num_stan(num_w)

    adress = ad_clean(adress)

    return city, school_type, num_street_name + ' ' + adress, num, postcode


# normalizowanie danych, uzyskiwanie
# tutaj dla ulatwienia wektory statyczne
norm_data_adress = [None for i in range(len(js_exl.index))]
norm_data_num = [None for i in range(len(js_exl.index))]
norm_data_postcode = [None for i in range(len(js_exl.index))]
norm_data_city = [None for i in range(len(js_exl.index))]
norm_data_sch_typ = [None for i in range(len(js_exl.index))]

for i in range(len(js_exl.index)):
    norm_data_city[i], norm_data_sch_typ[i], norm_data_adress[i], norm_data_num[i], norm_data_postcode[i] = find_adress(
        str(js_exl.iloc[i, 2]), str(js_exl.iloc[i, 3]), str(js_exl.iloc[i, 1]))

norm_data = {'ID': js_exl['INE_OS_ID'], 'Miejscowość': norm_data_city, 'Nazwa szkoły': js_exl['SZKOLA_SR'],
             'Nazwa typu': norm_data_sch_typ, 'Ulica': norm_data_adress, 'Nr domu': norm_data_num,
             'Kod poczt.': norm_data_postcode}
norm_data_js_exl = pd.DataFrame(data=norm_data)

norm_data_js_exl['Miejscowość'] = norm_data_js_exl['Miejscowość'].apply(dash_out)
norm_data_js_exl.loc[norm_data_js_exl['Miejscowość'] == 'nan'] = None
norm_data_js_exl.loc[norm_data_js_exl['Ulica'] == 'nan'] = None
norm_data_js_exl.loc[norm_data_js_exl['Nr domu'] == 'nan'] = None
norm_data_js_exl.loc[norm_data_js_exl['Kod poczt.'] == 'nan'] = None

norm_data_js_exl['ID'] = norm_data_js_exl['ID'].fillna(0.0).astype(float)
norm_data_js_exl['ID'] = norm_data_js_exl['ID'].astype(int)

norm_data_js_exl['PATRON'] = js_exl["PATRON"]

norm_data_js_exl.head(20)

# of_exl = of_exl.drop(columns=['Patron'])
of_exl['Miejscowość'] = of_exl['Miejscowość'].apply(dash_out)
of_exl.head(5)

of_exl = of_exl.reset_index(drop=True)
of_exl = of_exl.sort_values(by='Miejscowość')
dict_of_names = {}
for i in range(len(of_exl)):

    if str(of_exl.iloc[i, 3]) in dict_of_names:
        dict_of_names[str(of_exl.iloc[i, 3])].append(i)
    else:
        dict_of_names[str(of_exl.iloc[i, 3])] = [i]

print(dict_of_names)


def find2(i, lista):
    ac = 0
    dic_of_prop = {}

    id = norm_data_js_exl.iloc[i, 0]
    city = norm_data_js_exl.iloc[i, 1]
    school_name = norm_data_js_exl.iloc[i, 2]
    school_type = norm_data_js_exl.iloc[i, 3]
    street = norm_data_js_exl.iloc[i, 4]
    house_num = norm_data_js_exl.iloc[i, 5]
    pst_code = norm_data_js_exl.iloc[i, 6]

    for nr in lista:
        if is_string_empty(street) == False:
            fu = fuzz.partial_ratio(street, str(of_exl.iloc[nr, 4]))
            fu = fu / 100
        else:
            fu = 0

        if fu > 0.80:
            t = w_similar(school_type, of_exl.iloc[nr, 1])
            if t == None:
                t = 0

            d = w_similar(str(house_num), str(of_exl.iloc[nr, 5]))
            if d == None:
                d = 0

            if is_string_empty(school_name) == False:
                fs = fuzz.token_sort_ratio(school_name, of_exl.iloc[nr, 2])
                fs = fs / 100
            else:
                fs = 0

            ac = 1 * t + 4 * fu + 1 * d + 6 * fs

            ac = round((ac / 12.0) * 100, 2)

        if ac > 50 and fu > 0.80:
            dic_of_prop[of_exl.iloc[nr, 7]] = ac

    dic_of_prop_sorted = sorted(dic_of_prop.items(), key=lambda kv: kv[1], reverse=True)
    if len(dic_of_prop_sorted) == 0:
        return 'Prawdopodobnie błędne dane'
    else:
        return dic_of_prop_sorted[:5]


def is_string_empty(s):
    r = re.search('[a-zA-Z]', s)
    if r != None:
        return False
    else:
        return True


# MIN  - dolny zakres
# MAX  - gorny zakres danych z jsosa

MIN = 0
MAX = len(norm_data_js_exl)


def find():
    of_school_table = []
    of_school_org_table = []
    of_school_loc_table = []
    prop_table = []
    status = []
    rspo_table = []
    prop = {}
    test = {}
    for i in range(MIN, MAX):
        max_prop = 0
        ac_max_idx = 0
        ac = 0

        id = norm_data_js_exl.iloc[i, 0]
        city = norm_data_js_exl.iloc[i, 1]
        school_name = norm_data_js_exl.iloc[i, 2]
        school_type = norm_data_js_exl.iloc[i, 3]
        street = norm_data_js_exl.iloc[i, 4]
        house_num = norm_data_js_exl.iloc[i, 5]
        pst_code = norm_data_js_exl.iloc[i, 6]
        patron = norm_data_js_exl.iloc[i, 7]
        flaga = 0

        for key in dict_of_names.keys():
            if w_similar(norm_data_js_exl.iloc[i, 1], str(key)) == 1:
                miasto = str(key)
                flaga = 1
                break

        if flaga == 1:
            lista = dict_of_names[miasto]

            for nr in lista:

                m = w_similar(city, of_exl.iloc[nr, 3])
                if m == None:
                    m = 0

                t = w_similar(school_type, of_exl.iloc[nr, 1])
                if t == None:
                    t = 0

                d = w_similar(str(house_num), str(of_exl.iloc[nr, 5]))
                if d == None:
                    d = 0

                if is_string_empty(school_name) == False:
                    fs = fuzz.token_sort_ratio(school_name, of_exl.iloc[nr, 2])
                    fs = fs / 100
                else:
                    fs = 0

                if is_string_empty(street) == False:
                    fu = fuzz.partial_ratio(street, str(of_exl.iloc[nr, 4]))
                    fu = fu / 100
                else:
                    fu = 0

                # miasta musza sie zgadzac
                if m > 0.93 and fu != 0:
                    ac = 1 * t + 4 * fu + 1 * d + 6 * fs
                    ac = round((ac / 12.0) * 100, 2)

                elif m > 0.93:
                    if is_string_empty(patron) == False:
                        fp = fuzz.partial_ratio(patron, str(of_exl.iloc[nr, 8]))
                        fp = fp / 100
                    else:
                        fp = 0
                    ac = 1 * t + 4 * fs + 8 * fp
                    ac = round((ac / 13.0) * 100, 2)

                if ac > max_prop:
                    max_prop = ac
                    ac_max_idx = nr

            if max_prop < 50:
                of_school_loc_table.append('Brak wystarczających danych')
                status.append('Brak wystarczających danych')
                of_school_org_table.append("-")
                prop_table.append(max_prop)

            elif is_string_empty(street) == True and max_prop < 80:
                of_school_loc_table.append('Brak wystarczających danych')
                status.append('Brak wystarczających danych')
                of_school_org_table.append("-")
                prop_table.append(max_prop)

            elif max_prop < 87:
                prop_table.append('50-87')
                of_school_loc_table.append(of_exl.iloc[ac_max_idx, 3])
                status.append('niepewny')
                lista_proponowanych = find2(i, lista)
                of_school_org_table.append(lista_proponowanych)

            else:
                prop_table.append(str(max_prop))
                of_school_loc_table.append(of_exl.iloc[ac_max_idx, 3])
                status.append('pewny')
                of_school_org_table.append(of_exl.iloc[ac_max_idx, 7])

        elif flaga == 0:
            prop_table.append('Brak podanego miasta w bazie')
            of_school_loc_table.append('Brak podanego miasta w bazie')
            status.append('Brak podanego miasta w bazie')
            of_school_org_table.append('Brak podanego miasta w bazie')

        clear_output()
        print(((i - MIN) / (MAX - MIN)) * 100, '%')

    return of_school_loc_table, prop_table, status, of_school_org_table


of_exl = of_exl.sort_values(by='Miejscowość')
norm_data_loc_of_school, norm_data_prop, status_tab, norm_data_of_school_org = find()

final_data = {'ID kandydata': js_exl.iloc[MIN:MAX, 0], 'Miejscowość szkoły (wprowadzona)': js_exl.iloc[MIN:MAX, 2],
              'Miejscowość szkoły (znormalizowana)': norm_data_loc_of_school, 'Zgodność danych (%)': norm_data_prop,
              'Status': status_tab, 'Nazwa szkoły (niezmieniona)': js_kopia.iloc[MIN:MAX, 1],
              'Nazwa szkoły z bazy danych (niezmieniona)': norm_data_of_school_org}
norm_data_final = pd.DataFrame(data=final_data)
norm_data_final.head(50)

norm_data_final.to_excel('cale.xlsx')
files.download('cale.xlsx')

norm_data_js_exl.to_excel('norm_data_js_exl.xlsx')
files.download('norm_data_js_exl.xlsx')

of_tab = []
print(rspo_tab)
for i in range(len(rspo_tab)):
    rspo = rspo_tab[i]
    ff = of_kopia.loc[of_kopia['Nr RSPO'] == rspo]
    ff.reset_index()
    if ff.empty == False:
        result = ff.iloc[0, 3]
    else:
        result = None
    of_tab.append(result)


def insert_sort(tabl):
    tablnew = []
    z = 0
    for i in range(len(tabl)):
        for j in range(len(tablnew)):
            z = 0
            if tabl[i] > tablnew[j]:
                tablnew.insert(j, tabl[i])
                z = 1
                break
        if z == 0:
            tablnew.append(tabl[i])
    return tablnew


tabl = [-1000, 100, 100000, 400, 3242, -10000000, -1, -2, 5, 6, 11]
print(insert_sort(tabl))