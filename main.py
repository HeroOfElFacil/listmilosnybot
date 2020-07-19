import discord
from random import shuffle
from datetime import datetime
import re

class GraczObiekt:
    def __init__(self, dcuser):
        self.dcuser = dcuser
        self.reka = []
        self.pokojowka = False
        self.hardreset = False


def teraz():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

odrzucona_karta = ""
ingame = False
tokeny = open("tokeny.txt", encoding='utf-8').read().splitlines()
komendyhelp = open("help.txt", encoding='utf-8').read()
legenda = open("legenda.txt", encoding='utf-8').read()
talia = open("karty.txt", encoding='utf-8').read().splitlines()
gracze = []
kolejka = []
print(komendyhelp)
print(talia)
client = discord.Client()

wart_kart = {
    "Skrytobójca": 0,
    "Strażniczka": 1,
    "Ksiądz": 2,
    "Baron": 3,
    "Pokojówka": 4,
    "Książe": 5,
    "Król": 6,
    "Hrabina": 7,
    "Księżniczka": 8
}

nazwy = {
    "skrytobojca": "Skrytobójca",
    "strazniczka": "Strażniczka",
    "ksiadz": "Ksiądz",
    "baron": "baron",
    "pokojowka": "Pokojówka",
    "ksiaze": "Książe",
    "krol": "Król",
    "Hrabina": "hrabina",
    "ksiezniczka": "Księżniczka",
    "0": "Skrytobójca",
    "1": "Strażniczka",
    "2": "Ksiądz",
    "3": "baron",
    "4": "Pokojówka",
    "5": "Książe",
    "6": "Król",
    "7": "hrabina",
    "8": "Księżniczka"
}

tlumacz = str.maketrans("ęóąśłżźćń", "eoaslzzcn")

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global ingame
    global tokeny
    global komendyhelp
    global talia
    global gracze
    global kolejka
    global odrzucona_karta

    async def sprawdz_koniec_gry(message):
        global talia
        global ingame
        global kolejka
        global gracze
        if len(kolejka) <= 1:
            winner = kolejka[0].dcuser
            await message.channel.send(str(winner) + " wygrał!")
            ingame = False
            talia = open("karty.txt", encoding='utf-8').read().splitlines()
            kolejka = []
            gracze = []
            return
        if len(talia) == 0:
            winner = kolejka[0]
            for gracz in kolejka:
                if wart_kart[winner.reka[0]] < wart_kart[gracz.reka[0]]:
                    winner = gracz
            await message.channel.send(str(winner.dcuser) + " wygrał!")
            await message.channel.send("Jego karta to: " + str(winner.reka[0]))
            ingame = False
            talia = open("karty.txt", encoding='utf-8').read().splitlines()
            kolejka = []
            gracze = []

    def czy_jego_kolej(message):
        global ingame
        if ingame is not True:
            return False
        if kolejka[0].dcuser == message.author:
            return True

        return False


    async def gracz_kill(umieracz):
        global kolejka
        present = False
        for gracz in kolejka:
            if gracz.dcuser == umieracz:
                await message.channel.send(str(gracz.dcuser) + " odpada!")
                await message.channel.send("Jego ręka to: " + str(gracz.reka))
                tmp = gracz
                present = True
        if present:
            kolejka.remove(tmp)
        await sprawdz_koniec_gry(message)

    if message.author == client.user:
        return
    if message.content.startswith('!lmhelp'):
        print(teraz() + " " + str(message.author) + " !lmhelp")
        await message.channel.send(komendyhelp)
    if re.match("^!lm(legenda|info)", message.content):
        print(teraz() + " " + str(message.author) + " !lmlegenda")
        await message.channel.send(legenda)
    if re.match("^!lm(dolacz|join)", message.content):
        print(teraz() + " " + str(message.author) + " !lmdolacz")
        if ingame is not True:
            if message.author in gracze:
                msg = str(message.author) + " już jest w lobby"
            elif message.author not in gracze:
                if len(gracze) <= 8:
                    gracze.append(message.author)
                    print(gracze)
                    msg = str(message.author) + " dołączony do lobby"
                else:
                    msg = "Maksymalnie 8 graczy"
        elif ingame:
            msg = "Nie można dołączyć do trwającej gry"
        await message.channel.send(msg)

    if re.match("^!lm(opusc|leave)", message.content):
        print(teraz() + " " + str(message.author) + " !opusc")
        if ingame is not True:
            if message.author in gracze:
                gracze.remove(message.author)
                print(gracze)
                msg = str(message.author) + " usunięty z lobby"
            elif message.author not in gracze:
                msg = str(message.author) + " nie jest w lobby, nie moze zostac usuniety"
            await message.channel.send(msg)
        elif ingame:
            await gracz_kill(message.author)

    if message.content.startswith('!lmgracze'):
        print(teraz() + " " + str(message.author) + " !lmgracze")
        if not gracze:
            msg = "Lobby jest puste"
        else:
            msg = "Gracze w lobby: "
            for gracz in gracze:
                msg +=  str(gracz) + ", "
        await message.channel.send(msg)
    if message.content.startswith('!lmecho'):
        print(message.content)
        await message.channel.send(message.content)
        tmpid = int(message.content.split()[1][3:-1])
        print(tmpid)
        present = False
        for gracz in gracze:
            if gracz.id == tmpid:
                present = True
        if present:
            await message.channel.send("Gracz w grze")

    if message.content.startswith('!lmstart'):
        if ingame:
            await message.channel.send("Gra już trwa")
            return

        print(teraz() + " " + str(message.author) + " !lmstart")
        if len(gracze) >= 2:
            await message.channel.send("Gra rozpoczęta!")
        else:
            await message.channel.send("Niewystarczająca liczba graczy")
            return
        for gracz in gracze:
            kolejka.append(GraczObiekt(gracz))
        msg = "Gracze w grze: "
        shuffle(talia)
        odrzucona_karta = talia.pop(0) # wyrzucenie jednej karty
        kolejka[0].reka.append(talia.pop(0))
        for gracz in kolejka:
            msg += str(gracz.dcuser) + ", "
            gracz.reka.append(talia.pop(0))
            await gracz.dcuser.send(gracz.reka)
        await message.channel.send(msg)
        ingame = True

    if message.content.startswith('!lmreka'):
        print(teraz() + " " + str(message.author) + " !lmreka")
        if ingame is True:
            if message.author in gracze:
                for gracz in kolejka:
                    if message.author == gracz.dcuser:
                        await gracz.dcuser.send(gracz.reka)
                        await message.channel.send("Wysłano wiadomość")
        else:
            await message.channel.send("Nie trwa obecnie gra")

    if message.content.startswith('!lmreset'):
        print(teraz() + " " + str(message.author) + " !lmreset")
        if ingame is True:
            for gracz in kolejka:
                if message.author == gracz.dcuser:
                    gracz.hardreset = True
            hardreset = 0
            for gracz in kolejka:
                if gracz.hardreset is True:
                    hardreset += 1
            if hardreset >= len(kolejka)/2:
                ingame = False
                talia = open("karty.txt", encoding='utf-8').read().splitlines()
                kolejka = []
                gracze = []
                await message.channel.send("Gra zresetowana")
            else:
                await message.channel.send("Hard reset? **(" + str(hardreset) + "/" + str(len(kolejka)) + ")**")

        else:
            await message.channel.send("Nie trwa obecnie gra")

    if message.content.startswith('!lmkolejka'):
        print(teraz() + " " + str(message.author) + " !lmkolejka")
        msg = "Gracze w grze: "
        for gracz in kolejka:
            msg += str(gracz.dcuser) + ", "
        await message.channel.send(msg)

    if message.content.startswith('!lmpokojowki'):
        print(teraz() + " " + str(message.author) + " !lmpokojowki")
        msg = "Gracze z aktywną pokojówką: "
        for gracz in kolejka:
            if gracz.pokojowka:
                msg += str(gracz.dcuser) + ", "
        await message.channel.send(msg)

    if message.content.startswith('!lmile'):
        print(teraz() + " " + str(message.author) + " !lmile")
        if ingame:
            await message.channel.send("Zostało " + str(len(talia)) + " kart w talii")
        else:
            await message.channel.send("Nie trwa obecnie gra")

    async def nast_osoba():
        global kolejka
        global talia
        kolejka.append(kolejka.pop(0))
        kolejka[0].reka.append(talia.pop(0))
        await kolejka[0].dcuser.send(kolejka[0].reka)
        await message.channel.send("Teraz zagrywa " + str(kolejka[0].dcuser))

    def wyczysc_pokojowke(message):
        for gracz in kolejka:
            if gracz.dcuser == message.author:
                gracz.pokojowka = False

    async def sprawdz_pokojowke(target):
        global kolejka
        if target.pokojowka is True:
            await message.channel.send(str(target.dcuser) + " zagrał pokojówkę, nie może być wybrany")
            gracze_dost = False
            for gracz in kolejka:
                if gracz.dcuser != message.author and gracz.pokojowka is False:
                    gracze_dost = True
            if gracze_dost:
                return False
            else:
                await message.channel.send("Nie ma graczy, na których można by rzucić kartę, kolejka pominięta")
                await sprawdz_koniec_gry(message)
                await nast_osoba()
                return True
        return False

    if re.match("^!lm(0|skrytobojca)", message.content):
        wyczysc_pokojowke(message)
        print(teraz() + " " + str(message.author) + " !lmskrytobojca")
        if czy_jego_kolej(message) is not True:
            await message.channel.send("To nie twoja kolej, teraz zagrywa " + str(kolejka[0].dcuser))
            return
        if "Skrytobójca" not in kolejka[0].reka:
            await message.channel.send("Nie masz takiej karty!")
            return
        kolejka[0].reka.remove("Skrytobójca")
        await message.channel.send(str(kolejka[0].dcuser) + " zagrywa Skrytobójcę (0)")
        await sprawdz_koniec_gry(message)
        await nast_osoba()

    if re.match("^!lm(1|strazniczka)", message.content):
        wyczysc_pokojowke(message)
        print(teraz() + " " + str(message.author) + " !lmstrazniczka")
        if len(message.content.split()) != 3:
            await message.channel.send("Niepoprawna komenda!")
            return
        wartosc = message.content.split()[2]
        wartosc = nazwy[wartosc.lower().translate(tlumacz)]
        if re.match("(1|Strażniczka)",wartosc):
            await message.channel.send("Nie można targetować strażniczek")
            return
        if wartosc not in wart_kart.keys() and wartosc not in range(2, 9):
            await message.channel.send("Niepoprawny target")
            return
        if czy_jego_kolej(message) is not True:
            await message.channel.send("To nie twoja kolej, teraz zagrywa " + str(kolejka[0].dcuser))
            return
        if "Strażniczka" not in kolejka[0].reka:
            await message.channel.send("Nie masz takiej karty!")
            return
        kolejka[0].reka.remove("Strażniczka")
        target = int(message.content.split()[1][3:-1])

        if wartosc in wart_kart.keys():
            wartosc = wart_kart[wartosc]
        for gracz in kolejka:
            if gracz.dcuser.id == target:
                target = gracz
                break
        await message.channel.send(str(kolejka[0].dcuser) + " zagrywa Strażniczkę (1)")
        pokojowka = await sprawdz_pokojowke(target)
        if target.pokojowka is not True:
            if "Skrytobójca" in target.reka:
                await message.channel.send(str(target.dcuser) + " Miał skrytobójcę! Teraz też wymienia kartę!")
                target.reka.remove("Skrytobójca")
                if len(talia) > 0:
                    target.reka.append(talia.pop(0))
                else:
                    target.reka.append(odrzucona_karta)
                await gracz_kill(message.author)
            elif wart_kart[target.reka[0]] == int(wartosc):
                await message.channel.send("Trafiony!")
                await gracz_kill(target.dcuser)
            else:
                await message.channel.send("Pudło!")
        if ingame and pokojowka is not True:
            await sprawdz_koniec_gry(message)
            await nast_osoba()

    if re.match("^!lm(2|ksiadz)", message.content):
        wyczysc_pokojowke(message)
        print(teraz() + " " + str(message.author) + " !lmksiadz")
        if len(message.content.split()) != 2:
            await message.channel.send("Niepoprawna komenda!")
            return
        if czy_jego_kolej(message) is not True:
            await message.channel.send("To nie twoja kolej, teraz zagrywa " + str(kolejka[0].dcuser))
            return
        if "Ksiądz" not in kolejka[0].reka:
            await message.channel.send("Nie masz takiej karty!")
            return
        kolejka[0].reka.remove("Ksiądz")
        target = int(message.content.split()[1][3:-1])
        for gracz in kolejka:
            if gracz.dcuser.id == target:
                target = gracz
                break
        await message.channel.send(str(kolejka[0].dcuser) + " zagrywa Księdza (2) i poznaje kartę " + str(target.dcuser))
        pokojowka = await sprawdz_pokojowke(target)
        if target.pokojowka is not True:
            await message.author.send("Ręka " + str(target.dcuser) + " to " + str(target.reka))
        if pokojowka is not True:
            await sprawdz_koniec_gry(message)
            await nast_osoba()

    if re.match("^!lm(3|baron)", message.content):
        wyczysc_pokojowke(message)
        print(teraz() + " " + str(message.author) + " !lmbaron")
        if len(message.content.split()) != 2:
            await message.channel.send("Niepoprawna komenda!")
            return
        if czy_jego_kolej(message) is not True:
            await message.channel.send("To nie twoja kolej, teraz zagrywa " + str(kolejka[0].dcuser))
            return
        if "Baron" not in kolejka[0].reka:
            await message.channel.send("Nie masz takiej karty!")
            return
        kolejka[0].reka.remove("Baron")
        target = int(message.content.split()[1][3:-1])
        for gracz in kolejka:
            if gracz.dcuser.id == target:
                target = gracz
            if gracz.dcuser == message.author:
                autor = gracz
        await message.channel.send(str(kolejka[0].dcuser) + " zagrywa Barona (3)")
        pokojowka = await sprawdz_pokojowke(target)
        if target.pokojowka is not True:
            await message.author.send("Ręka " + str(target.dcuser) + " to " + str(target.reka))
            await target.dcuser.send("Ręka " + str(autor.dcuser) + " to " + str(autor.reka))
            if wart_kart[target.reka[0]] < wart_kart[autor.reka[0]]:
                await message.channel.send(str(autor.dcuser) + " wygrał")
                await gracz_kill(target.dcuser)
            elif wart_kart[target.reka[0]] > wart_kart[autor.reka[0]]:
                await message.channel.send(str(target.dcuser) + " wygrał")
                await gracz_kill(autor.dcuser)
            elif wart_kart[target.reka[0]] == wart_kart[autor.reka[0]]:
                await message.channel.send("Remis!")
        if ingame and pokojowka is not True:
            await sprawdz_koniec_gry(message)
            await nast_osoba()

    if re.match("^!lm(4|pokojowka)", message.content):
        wyczysc_pokojowke(message)
        print(teraz() + " " + str(message.author) + " !lmpokojowka")
        if czy_jego_kolej(message) is not True:
            await message.channel.send("To nie twoja kolej, teraz zagrywa " + str(kolejka[0].dcuser))
            return
        if "Pokojówka" not in kolejka[0].reka:
            await message.channel.send("Nie masz takiej karty!")
            return
        kolejka[0].reka.remove("Pokojówka")
        await message.channel.send(str(kolejka[0].dcuser) + " zagrywa Pokojówkę (4)")
        kolejka[0].pokojowka = True
        await sprawdz_koniec_gry(message)
        await nast_osoba()

    if re.match("^!lm(5|ksiaze)", message.content):
        wyczysc_pokojowke(message)
        print(teraz() + " " + str(message.author) + " !lmksiaze")
        for gracz in kolejka:
            if gracz.dcuser == message.author:
                autor = gracz
                break
        if "Hrabina" in autor.reka:
            await message.channel.send("Nie możesz zagrać tej karty")
            return

        if len(message.content.split()) != 2:
            await message.channel.send("Niepoprawna komenda!")
            return
        if czy_jego_kolej(message) is not True:
            await message.channel.send("To nie twoja kolej, teraz zagrywa " + str(kolejka[0].dcuser))
            return
        if "Książe" not in kolejka[0].reka:
            await message.channel.send("Nie masz takiej karty!")
            return
        kolejka[0].reka.remove("Książe")
        target = int(message.content.split()[1][3:-1])
        for gracz in kolejka:
            if gracz.dcuser.id == target:
                target = gracz
                break
        await message.channel.send(str(kolejka[0].dcuser) + " zagrywa Księcia (5)")
        pokojowka = await sprawdz_pokojowke(target)
        if target.pokojowka is not True:
            await message.channel.send(str(target.dcuser) + "odrzuca z ręki kartę: " + target.reka.pop(0))
            if len(talia) > 0:
                target.reka.append(talia.pop(0))
            else:
                target.reka.append(odrzucona_karta)
        if ingame and pokojowka is not True:
            await sprawdz_koniec_gry(message)
            await nast_osoba()

    if re.match("^!lm(6|krol)", message.content):
        wyczysc_pokojowke(message)
        print(teraz() + " " + str(message.author) + " !lmkrol")
        for gracz in kolejka:
            if gracz.dcuser == message.author:
                autor = gracz
                break
        if "Hrabina" in autor.reka:
            await message.channel.send("Nie możesz zagrać tej karty")
            return
        if len(message.content.split()) != 2:
            await message.channel.send("Niepoprawna komenda!")
            return
        if czy_jego_kolej(message) is not True:
            await message.channel.send("To nie twoja kolej, teraz zagrywa " + str(kolejka[0].dcuser))
            return
        if "Król" not in kolejka[0].reka:
            await message.channel.send("Nie masz takiej karty!")
            return
        kolejka[0].reka.remove("Król")
        target = int(message.content.split()[1][3:-1])
        for gracz in kolejka:
            if gracz.dcuser.id == target:
                target = gracz
                break
        await message.channel.send(str(kolejka[0].dcuser) + " zagrywa Króla (6)")
        pokojowka = await sprawdz_pokojowke(target)
        if target.pokojowka is not True:
            autor.reka, target.reka = target.reka, autor.reka
        await autor.dcuser.send("Twoja ręka po wymianie: " + str(autor.reka))
        await target.dcuser.send("Twoja ręka po wymianie: " + str(target.reka))
        if ingame and pokojowka is not True:
            await sprawdz_koniec_gry(message)
            await nast_osoba()

    if re.match("^!lm(7|hrabina)", message.content):
        wyczysc_pokojowke(message)
        print(teraz() + " " + str(message.author) + " !lmhraibna")
        if czy_jego_kolej(message) is not True:
            await message.channel.send("To nie twoja kolej, teraz zagrywa " + str(kolejka[0].dcuser))
            return
        if "Hrabina" not in kolejka[0].reka:
            await message.channel.send("Nie masz takiej karty!")
            return
        kolejka[0].reka.remove("Hrabina")
        await message.channel.send(str(kolejka[0].dcuser) + " zagrywa Hrabinę (7)")
        await sprawdz_koniec_gry(message)
        await nast_osoba()

client.run(tokeny[0])