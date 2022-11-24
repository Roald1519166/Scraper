# %%
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
from selenium import webdriver
from tqdm import tqdm , trange
import time
import datetime
pd.__version__

# %%
## Dataset variabele
dataset = './Data/huurwoningentotaalvoorpowerbi.xlsx'
## Ophalen van de datasets
oud = pd.read_excel(dataset)
oud.drop(oud[oud['Status'] == 'Inactive'].index, inplace=True)
oud = oud.fillna("")
oud["Status"] = "TBD"
pd.set_option('display.max_columns', None)

# %%
oud

# %%
## Huidige datum krijgen (Jaar-Maand-Dag)
now = datetime.datetime.now()
current_time = now.strftime("%Y-%m-%d")
current_time

# %%
url = "https://www.huurwoningen.nl/aanbod-huurwoningen/?page=1/" + "?page="

r = requests.get(url)
soup = bs(r.content)
contents = soup.prettify()
# print(contents)
totaal = soup.find(class_="search-list")
# print(totaal.prettify())

# %%
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

for pagina in trange(int(totpages)):
    url = "https://www.huurwoningen.nl/aanbod-huurwoningen/?page=" + str(pagina)

    r = requests.get(url)
    soup = bs(r.content)
    contents = soup.prettify()
    # print(contents)
    totaal = soup.find(class_="search-list")
    # print(totaal.prettify())

    linktitle = soup.select(".listing-search-item__title a")
    subtitle = soup.select(".listing-search-item__sub-title")
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
    # print(pagina)
    time.sleep(0.3)

# %%
prijs2 = []
for i in prijs:
    prijs2.append(i.replace(".",""))

# %%
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
df

# %%
merged = pd.merge(df, oud, on='Link', indicator=True, how ='outer')
datadif = merged.loc[lambda x : x['_merge'] != 'both']

# %%
dfdif1 = datadif.loc[datadif['_merge'] == 'left_only']
dfdif2 = datadif.loc[datadif['_merge'] == 'right_only']
di1 = oud[0:0]
di2 = oud[0:0]


# %%
prijsy = []
for i in dfdif2['Prijs_y']:
    prijsy.append(str(i).split('.0')[0])
dfdif2['Prijs_y'] = prijsy
oppervlaktey = []
for i in dfdif2['Oppervlakte_y']:
    oppervlaktey.append(str(i).split('.0')[0])
dfdif2['Oppervlakte_y'] = oppervlaktey
kamersy = []
for i in dfdif2['Kamers_y']:
    kamersy.append(str(i).split('.0')[0])
dfdif2['Kamers_y'] = kamersy
bouwjaary = []
for i in dfdif2['Bouwjaar']:
    bouwjaary.append(str(i).split('.0')[0])
dfdif2['Bouwjaar'] = bouwjaary

# %%
di1["Plek"] = dfdif1["Plek_x"]
di1["Wijk"] = dfdif1["Wijk_x"]
di1["Postcode"] = dfdif1["Postcode_x"]
di1["Plaatsnaam"] = dfdif1["Plaatsnaam_x"]
di1["Prijs"] = dfdif1["Prijs_x"]
di1["Oppervlakte"] = dfdif1["Oppervlakte_x"]
di1["Kamers"] = dfdif1["Kamers_x"]
di1["Interieur"] = dfdif1["Interieur_x"]
di1["Link"] = dfdif1["Link"]
di1["Updated"] = current_time
di1["Status"] = 'Active'
di1 = di1.reset_index()

di2["Plek"] = dfdif2["Plek_y"]
di2["Wijk"] = dfdif2["Wijk_y"]
di2["Postcode"] = dfdif2["Postcode_y"]
di2["Plaatsnaam"] = dfdif2["Plaatsnaam_y"]
di2["Prijs"] = dfdif2["Prijs_y"]
di2["Oppervlakte"] = dfdif2["Oppervlakte_y"]
di2["Kamers"] = dfdif2["Kamers_y"]
di2["Interieur"] = dfdif2["Interieur_y"]
di2["Link"] = dfdif2["Link"]
di2["AangebodenSinds"] = dfdif2["AangebodenSinds"]
di2["Beschikbaarheid"] = dfdif2["Beschikbaarheid"]
di2["Woningtype"] = dfdif2["Woningtype"]
di2["Bouwjaar"] = dfdif2["Bouwjaar"]
di2["Parkeren"] = dfdif2["Parkeren"]
di2["Updated"] = dfdif2["Updated"]
di2["Status"] = 'Inactive'
di2 = di2.reset_index()
di2 = di2.drop(columns='index')

# %%
sinds = []
beschikbaar = []
woningtype = []
jaarbouw = []
parkeer = []

for i in trange(len(di1["Link"])):
    url = str(di1["Link"][i])

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
    

# %%
di1["AangebodenSinds"] = sinds
di1["Beschikbaarheid"] = beschikbaar
di1["Woningtype"] = woningtype
di1["Bouwjaar"] = jaarbouw
di1["Parkeren"] = parkeer
di1.drop_duplicates()
di1 = di1.drop(columns='index')

# %%
inner1 = pd.concat([oud, di1])
inner1.loc[inner1.duplicated(keep=False), :]

# %%
inner1.drop_duplicates(keep='first').shape
inner2 = pd.concat([inner1, di2])
inner2 = inner2.drop_duplicates(keep='last')
inner2["Status"].value_counts()

# %%
inner2["Status"] = inner2["Status"].replace("Active","New")
inner2["Status"] = inner2["Status"].replace("TBD","Active")
inner2["Status"].value_counts()

# %%
bouwjaary = []
for i in inner2['Bouwjaar']:
    bouwjaary.append(str(i).split('.0')[0])
inner2['Bouwjaar'] = bouwjaary

# %%
oud = oud.fillna("")

# %%
name = './Data/huurwoningentotaal'
inner2.to_excel(name + current_time + ".xlsx", index=False)
inner2.to_excel(name + 'voorpowerbi' + ".xlsx", index=False)


