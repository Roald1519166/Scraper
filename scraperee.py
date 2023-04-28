## Importeren libraries
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
from selenium import webdriver
from tqdm import tqdm , trange
import time
import datetime
pd.__version__

## Dataset variabele
dataset = './Data/huurwoningentotaalvoorpowerbi.xlsx'
## Ophalen van de datasets
oud = pd.read_excel(dataset)
## Weghalen van oude inactieve
oud = oud.fillna("")
print(oud["Status"].value_counts())
oud["Status"] = "TBD"
pd.set_option('display.max_columns', None)

## Huidige datum krijgen (Jaar-Maand-Dag)
now = datetime.datetime.now()
current_time = now.strftime("%m-%d-%Y %H:%M:%S")
current_time

url = "https://www.huurwoningen.nl/aanbod-huurwoningen/?page=1/" + "?page="

r = requests.get(url)
soup = bs(r.content)
contents = soup.prettify()
totaal = soup.find(class_="search-list")

pagina = 1
link = []
title=[]
plek=[]
adres=[]
prijs=[]
oppervlakte = []
kamers = []
interieur = []
totpages = soup.select(".pagination__item a")[4].text

## Scrapen van alle huurwoningen, niet alle data
for pagina in trange(int(totpages)):
    url = "https://www.huurwoningen.nl/aanbod-huurwoningen/?page=" + str(pagina)

    r = requests.get(url)
    soup = bs(r.content)
    contents = soup.prettify()
    totaal = soup.find(class_="search-list")
    linktitle = soup.select(".listing-search-item__title a")
    subtitle = soup.select("div.listing-search-item__sub-title\\'")
    prijstitle = soup.select(".listing-search-item__price")
    info = soup.select(".listing-search-item__features")

    i = 0

    for i in range(len(linktitle)):
        link.append('https://www.huurwoningen.nl' + linktitle[i]['href'])
        title.append(linktitle[i].text.strip())
        plek.append(subtitle[i].text.strip().split(' ',3)[3].replace('(','').replace(')',''))
        adres.append(subtitle[i].text.strip().split(' (')[0])
        prijs.append(prijstitle[i].text.strip().split(' ')[0][2:])
        m2 = info[i].select(".illustrated-features__item--surface-area")
        oppervlakte.append(m2[0].text.split(' ')[0])
        rooms = info[i].select(".illustrated-features__item--number-of-rooms")
        try : 
            kamers.append(rooms[0].text.split(' ')[0])
        except IndexError:
            kamers.append("")
        intr = info[i].select(".illustrated-features__item--interior")
        try :
            interieur.append(intr[0].text)
        except IndexError:
            interieur.append("")
        i = i + 1
    pagina = pagina + 1
    time.sleep(0.3)

## Gescrapte data in DF gooien
prijs2 = []
for i in prijs:
    prijs2.append(i.replace(".",""))

df = pd.DataFrame()
prijs2 = []
for i in prijs:
    prijs2.append(i.replace(".",""))
df["Plek"] = title
df["Wijk"] = plek
df["Postcode"] = adres
df["Plaatsnaam"] = df["Postcode"].str.split(' ',n=2).str[2]
df["Postcode"] = df["Postcode"].str.split(' ').str[0] + " " +  df["Postcode"].str.split(' ').str[1]
df["Prijs"] = prijs2
df["Oppervlakte"] = oppervlakte
df["Kamers"] = kamers
df["Interieur"] = interieur
df["Link"] = link
df.drop_duplicates()

## Mergen en kijken naar verschillen
merged = pd.merge(df, oud, on='Link', indicator=True, how ='outer')
datadif = merged.loc[lambda x : x['_merge'] != 'both']
both = merged.loc[lambda x : x['_merge'] == 'both']
bestaand = oud[oud.index.isin(list(both.index))]
bestaand["Status"] = 'Active'

left_only = datadif.loc[datadif['_merge'] == 'left_only']
right_only = datadif.loc[datadif['_merge'] == 'right_only']
nieuw = oud[0:0]
inactief = oud[0:0]

## Schoonmaken van ongewilde punten
prijsy = []
for i in right_only['Prijs_y']:
    prijsy.append(str(i).split('.0')[0])
right_only['Prijs_y'] = prijsy
oppervlaktey = []
for i in right_only['Oppervlakte_y']:
    oppervlaktey.append(str(i).split('.0')[0])
right_only['Oppervlakte_y'] = oppervlaktey
kamersy = []
for i in right_only['Kamers_y']:
    kamersy.append(str(i).split('.0')[0])
right_only['Kamers_y'] = kamersy
bouwjaary = []
for i in right_only['Bouwjaar']:
    bouwjaary.append(str(i).split('.0')[0])
right_only['Bouwjaar'] = bouwjaary

## Uit de merge de juiste definities gooien
nieuw["Plek"] = left_only["Plek_x"]
nieuw["Wijk"] = left_only["Wijk_x"]
nieuw["Postcode"] = left_only["Postcode_x"]
nieuw["Plaatsnaam"] = left_only["Plaatsnaam_x"]
nieuw["Prijs"] = left_only["Prijs_x"]
nieuw["Oppervlakte"] = left_only["Oppervlakte_x"]
nieuw["Kamers"] = left_only["Kamers_x"]
nieuw["Interieur"] = left_only["Interieur_x"]
nieuw["Link"] = left_only["Link"]
nieuw["Updated"] = current_time
nieuw["Status"] = 'New'
nieuw = nieuw.reset_index()
nieuw = nieuw.drop(columns='index')

## Insgelijks
inactief["Plek"] = right_only["Plek_y"]
inactief["Wijk"] = right_only["Wijk_y"]
inactief["Postcode"] = right_only["Postcode_y"]
inactief["Plaatsnaam"] = right_only["Plaatsnaam_y"]
inactief["Prijs"] = right_only["Prijs_y"]
inactief["Oppervlakte"] = right_only["Oppervlakte_y"]
inactief["Kamers"] = right_only["Kamers_y"]
inactief["Interieur"] = right_only["Interieur_y"]
inactief["Link"] = right_only["Link"]
inactief["AangebodenSinds"] = right_only["AangebodenSinds"]
inactief["Beschikbaarheid"] = right_only["Beschikbaarheid"]
inactief["Woningtype"] = right_only["Woningtype"]
inactief["Bouwjaar"] = right_only["Bouwjaar"]
inactief["Parkeren"] = right_only["Parkeren"]
inactief["Updated"] = right_only["Updated"]
inactief["Status"] = 'Inactive'
inactief['Outdated'] = current_time
inactief = inactief.reset_index()
inactief = inactief.drop(columns='index')

## Tweede iteratie, alleen ophalen van hetgeen wat nog niet verzameld is
sinds = []
beschikbaar = []
woningtype = []
jaarbouw = []
parkeer = []

for i in trange(len(nieuw["Link"])):
    url = str(nieuw["Link"][i])

    r = requests.get(url)
    soup = bs(r.content)
    contents = soup.prettify()
    # print(contents)
    totaal = soup.find(class_="page__row page__row--features")
    # print(totaal.prettify())

    aangebodensinds = soup.select(".listing-features__description--offered_since")
    beschikbaarheid = soup.select(".listing-features__description--acceptance")
    typewoning = soup.select(".listing-features__description--dwelling_type")
    bouwjaar = soup.select(".listing-features__description--construction_period")
    parkeren = soup.select(".listing-features__description--available")
    archivatie = soup.select('.listing-label--archived')

    try: 
        sinds.append(aangebodensinds[0].text.strip())
    except IndexError:
        sinds.append("")
    try:
        beschikbaar.append(beschikbaarheid[0].text.strip())
    except IndexError:
        beschikbaar.append("")
    try:
        woningtype.append(typewoning[0].text.strip().split()[0])
    except IndexError:
        woningtype.append("")
    try: 
        jaarbouw.append(bouwjaar[0].text.strip())
    except IndexError:
        jaarbouw.append("")
    try: 
        parkeer.append(parkeren[0].text.strip())
    except:
        parkeer.append("")

    i = i + 1
    time.sleep(0.3)
    
## Nieuwe gescrapte data toevoegen aan set
nieuw["AangebodenSinds"] = sinds
nieuw["Beschikbaarheid"] = beschikbaar
nieuw["Woningtype"] = woningtype
nieuw["Bouwjaar"] = jaarbouw
nieuw["Parkeren"] = parkeer
nieuw = nieuw.drop_duplicates()

## Bestaande en nieuwe appartementen in een dataset gooien
inner = pd.concat([bestaand, nieuw])
bouwjaary = []
for i in inner['Bouwjaar']:
    bouwjaary.append(str(i).split('.0')[0])
inner['Bouwjaar'] = bouwjaary
kamertjes = []
for i in inner['Kamers']:
    kamertjes.append(str(i).split('.0')[0])
inner['Kamers'] = kamertjes


inactievedf = './Data/huurwoningentotaalinactieftot.xlsx'
dfinactief = pd.read_excel(inactievedf)
dfinactiefdef = pd.concat([dfinactief, inactief])

## Exporteren data
name = './Data/huurwoningentotaal'
# inactief.to_excel(name + current_time + '_inactief.xlsx', index=False)
inner.to_excel(name + current_time + ".xlsx", index=False)
inner.to_csv(name + 'voorpowerbi' + ".csv", index=False)
inner.to_excel(name + 'voorpowerbi' + ".xlsx", index=False)
dfinactiefdef.to_excel(name + 'inactieftot' + ".xlsx", index=False)
dfinactiefdef.to_csv(name + 'inactieftot' + ".csv", index=False)
