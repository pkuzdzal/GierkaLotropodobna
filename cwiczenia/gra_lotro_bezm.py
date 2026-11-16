import tkinter as tk
import time
import random


# ==========================================
# KLASY I LOGIKA OBIEKTÓW
# ==========================================
class Entity:
    def __init__(self, canvas, x, y, size, color, hp):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.canvas = canvas
        self.hp = hp
        self.max_hp = hp
        self.ekwipunek = []
        self.id = None
        self.utworz_grafike()

    def utworz_grafike(self):
        self.id = self.canvas.create_rectangle(
            self.x - self.size,
            self.y - self.size,
            self.x + self.size,
            self.y + self.size,
            fill=self.color
        )

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.canvas.coords(
            self.id,
            self.x - self.size, self.y - self.size,
            self.x + self.size, self.y + self.size
        )
        for przedmiot in self.ekwipunek:
            przedmiot.aktualizuj_pozycje()

    def ustaw_pozycje(self, x, y):
        self.move(x - self.x, y - self.y)

    def dodaj_przedmiot(self, przedmiot):
        self.ekwipunek.append(przedmiot)

    def uzyj_przedmiotow(self, enemies):
        for przedmiot in self.ekwipunek:
            przedmiot.uzyj(enemies)


# ==========================================
# PRZEDMIOTY I BRONIE
# ==========================================
class ObszarObrazen:
    def __init__(self, canvas, wlasciciel, promien=50, dps=20 / 3):
        self.canvas = canvas
        self.wlasciciel = wlasciciel
        self.promien = promien
        self.obrazenia_na_klatke = dps * 0.03
        self.id = canvas.create_oval(
            wlasciciel.x - promien,
            wlasciciel.y - promien,
            wlasciciel.x + promien,
            wlasciciel.y + promien,
            outline="cyan",
            width=2
        )
        self.canvas.tag_lower(self.id, wlasciciel.id)

    def aktualizuj_pozycje(self):
        self.canvas.coords(
            self.id,
            self.wlasciciel.x - self.promien,
            self.wlasciciel.y - self.promien,
            self.wlasciciel.x + self.promien,
            self.wlasciciel.y + self.promien
        )

    def uzyj(self, enemies):
        for wrog in enemies[:]:
            dx = wrog.x - self.wlasciciel.x
            dy = wrog.y - self.wlasciciel.y
            dystans = (dx ** 2 + dy ** 2) ** 0.5

            if dystans <= self.promien + wrog.size:
                wrog.hp -= self.obrazenia_na_klatke
                if wrog.hp <= 0:
                    self.canvas.delete(wrog.id)
                    enemies.remove(wrog)


class Apteczka:
    def __init__(self, canvas, x, y, leczenie=20, size=6):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.leczenie = leczenie
        self.size = size
        self.id = None
        self.utworz_grafike()

    def utworz_grafike(self):
        self.id = self.canvas.create_oval(
            self.x - self.size,
            self.y - self.size,
            self.x + self.size,
            self.y + self.size,
            fill="lime",
            outline="white"
        )

    def podnies(self, gracz):
        gracz.hp = min(gracz.max_hp, gracz.hp + self.leczenie)
        self.canvas.delete(self.id)


# ==========================================
# MAPA I LOGIKA PRZECIWNIKÓW
# ==========================================
class Mapa:
    def __init__(self, canvas, pokoj_x, pokoj_y, hp_text_id, gracz):
        self.canvas = canvas
        self.pokoj_x = pokoj_x
        self.pokoj_y = pokoj_y
        self.hp_text_id = hp_text_id
        self.enemies = [Entity(canvas, 40, 40, 5, "red", 10)]
        self.zrespieni_wrogowie = 1
        self.przedmioty_na_ziemi = []
        self.wyjscia_id = []
        self.generuj_przedmioty(gracz)

    def rysuj_wyjscia(self):
        self.wyczysc_wyjscia()
        if self.pokoj_y > 0:
            self.wyjscia_id.append(self.canvas.create_rectangle(270, 0, 330, 10, fill="black", outline="black"))
        if self.pokoj_y < 4:
            self.wyjscia_id.append(self.canvas.create_rectangle(270, 390, 330, 400, fill="black", outline="black"))
        if self.pokoj_x > 0:
            self.wyjscia_id.append(self.canvas.create_rectangle(0, 170, 10, 230, fill="black", outline="black"))
        if self.pokoj_x < 4:
            self.wyjscia_id.append(self.canvas.create_rectangle(590, 170, 600, 230, fill="black", outline="black"))

    def wyczysc_wyjscia(self):
        for item_id in self.wyjscia_id:
            self.canvas.delete(item_id)
        self.wyjscia_id.clear()

    def ukryj_zawartosc(self):
        self.wyczysc_wyjscia()
        for wrog in self.enemies:
            self.canvas.delete(wrog.id)
        for przedmiot in self.przedmioty_na_ziemi:
            self.canvas.delete(przedmiot.id)

    def pokaz_zawartosc(self):
        self.rysuj_wyjscia()
        for wrog in self.enemies:
            wrog.utworz_grafike()
        for przedmiot in self.przedmioty_na_ziemi:
            przedmiot.utworz_grafike()

    def generuj_przedmioty(self, gracz):
        ile = random.randint(0, 2)
        rozmiar_apteczki = 6

        for _ in range(ile):
            for _ in range(50):
                x = random.randint(30, 570)
                y = random.randint(30, 370)

                if ((x - gracz.x) ** 2 + (y - gracz.y) ** 2) ** 0.5 < gracz.size + rozmiar_apteczki + 10:
                    continue

                if any(((x - p.x) ** 2 + (y - p.y) ** 2) ** 0.5 < p.size + rozmiar_apteczki + 10 for p in self.przedmioty_na_ziemi):
                    continue

                self.przedmioty_na_ziemi.append(Apteczka(self.canvas, x, y, size=rozmiar_apteczki))
                break

    def move_enemies(self, gracz):
        for i in self.enemies:
            dx = gracz.x - i.x
            dy = gracz.y - i.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            speed = 3

            if distance > speed:
                i.move((dx / distance) * speed, (dy / distance) * speed)
            elif distance > 0:
                i.move(dx, dy)

        for i in range(len(self.enemies)):
            for j in range(i + 1, len(self.enemies)):
                e1 = self.enemies[i]
                e2 = self.enemies[j]

                dx = e1.x - e2.x
                dy = e1.y - e2.y
                distance = (dx ** 2 + dy ** 2) ** 0.5
                min_distance = e1.size + e2.size + 4

                if 0 < distance < min_distance:
                    push_x = (dx / distance) * 1.5
                    push_y = (dy / distance) * 1.5
                    e1.move(push_x, push_y)
                    e2.move(-push_x, -push_y)
                elif distance == 0:
                    e1.move(1.5, 0)
                    e2.move(-1.5, 0)

    def check_collision(self, gracz):
        for i in self.enemies:
            dx = i.x - gracz.x
            dy = i.y - gracz.y
            if abs(dx) < 15 and abs(dy) < 15:
                gracz.hp -= 1
                self.canvas.itemconfig(self.hp_text_id, text=f"HP: {gracz.hp}")

        for przedmiot in self.przedmioty_na_ziemi[:]:
            dx = przedmiot.x - gracz.x
            dy = przedmiot.y - gracz.y
            if ((dx ** 2 + dy ** 2) ** 0.5) <= gracz.size + przedmiot.size:
                przedmiot.podnies(gracz)
                self.przedmioty_na_ziemi.remove(przedmiot)
                self.canvas.itemconfig(self.hp_text_id, text=f"HP: {gracz.hp}")


# ==========================================
# KONFIGURACJA OKNA I OBIEKTÓW STARTOWYCH
# ==========================================
okno = tk.Tk(baseName="Gra Lotropodobna")
okno.title("Gra Lotropodobna")
okno.geometry("600x400")
okno.resizable(False, False)
okno.configure(background="black")

canvas = tk.Canvas(okno, width=600, height=400, bg="grey")
canvas.pack()

gracz = None
swiat = {}
lokacja = None
pozycja_pokoju = (2, 2)
hp_text_id = None
klawisze = {}
predkosc = 5
lklatek = 0
gra_aktywna = False


def pokaz_menu():
    canvas.delete("all")
    canvas.create_rectangle(10, 10, 590, 390, fill="black")
    canvas.create_text(300, 140, text="GRA LOTROPODOBNA", fill="white", font=("Arial", 22, "bold"))

    btn_start = tk.Button(okno, text="NOWA GRA", font=("Arial", 14, "bold"), command=start_gry)
    canvas.create_window(300, 220, window=btn_start)


def zmien_pokoj(kierunek):
    global lokacja, pozycja_pokoju, lklatek
    px, py = pozycja_pokoju

    if kierunek == "gora" and py > 0:
        nowe_wsp = (px, py - 1)
        nowy_x, nowy_y = 300, 375
    elif kierunek == "dol" and py < 4:
        nowe_wsp = (px, py + 1)
        nowy_x, nowy_y = 300, 25
    elif kierunek == "lewo" and px > 0:
        nowe_wsp = (px - 1, py)
        nowy_x, nowy_y = 575, 200
    elif kierunek == "prawo" and px < 4:
        nowe_wsp = (px + 1, py)
        nowy_x, nowy_y = 25, 200
    else:
        return

    lokacja.ukryj_zawartosc()
    pozycja_pokoju = nowe_wsp
    gracz.ustaw_pozycje(nowy_x, nowy_y)
    lklatek = 0

    if pozycja_pokoju not in swiat:
        swiat[pozycja_pokoju] = Mapa(canvas, pozycja_pokoju[0], pozycja_pokoju[1], hp_text_id, gracz)
        lokacja = swiat[pozycja_pokoju]
        lokacja.rysuj_wyjscia()
    else:
        lokacja = swiat[pozycja_pokoju]
        lokacja.pokaz_zawartosc()


def start_gry():
    global gracz, swiat, lokacja, pozycja_pokoju, hp_text_id, lklatek, gra_aktywna, klawisze
    canvas.delete("all")
    canvas.create_rectangle(10, 10, 590, 390, fill="black")

    klawisze.clear()
    swiat.clear()
    lklatek = 0
    gra_aktywna = True
    pozycja_pokoju = (2, 2)

    gracz = Entity(canvas, x=300, y=200, size=10, color="blue", hp=100)
    gracz.dodaj_przedmiot(ObszarObrazen(canvas, gracz, promien=50))

    hp_text_id = canvas.create_text(50, 30, fill="lightblue", text=f"HP: {gracz.hp}", font=("Arial", 12, "bold"))

    lokacja = Mapa(canvas, 2, 2, hp_text_id, gracz)
    lokacja.rysuj_wyjscia()
    swiat[pozycja_pokoju] = lokacja
    game_loop()


def koniec_gry(kolor_tekstu):
    global gra_aktywna
    gra_aktywna = False
    canvas.create_text(300, 180, text="KONIEC GRY", fill=kolor_tekstu, font=("Arial", 24, "bold"))
    okno.after(2000, pokaz_menu)


# ==========================================
# STEROWANIE
# ==========================================
def nacisniecie(event):
    klawisze[event.keysym.lower()] = True


def puszczenie(event):
    klawisze[event.keysym.lower()] = False


okno.bind("<KeyPress>", nacisniecie)
okno.bind("<KeyRelease>", puszczenie)


# ==========================================
# GŁÓWNA PĘTLA GRY
# ==========================================
def game_loop():
    global lklatek
    if not gra_aktywna:
        return

    czas_startu = time.perf_counter()
    lklatek += 1

    lokacja.check_collision(gracz)
    lokacja.move_enemies(gracz)
    gracz.uzyj_przedmiotow(lokacja.enemies)

    if gracz.hp <= 0:
        koniec_gry("red")
        return

    dx = (1 if klawisze.get("d") else 0) - (1 if klawisze.get("a") else 0)
    dy = (1 if klawisze.get("s") else 0) - (1 if klawisze.get("w") else 0)

    if dx != 0 and dy != 0:
        dx *= 0.75
        dy *= 0.75

    if dx != 0 or dy != 0:
        ruch_x = dx * predkosc
        ruch_y = dy * predkosc

        if gracz.x + ruch_x - gracz.size <= 10:
            if 170 <= gracz.y <= 230 and pozycja_pokoju[0] > 0:
                zmien_pokoj("lewo")
                ruch_x = 0
            else:
                ruch_x = 10 + gracz.size - gracz.x
        elif gracz.x + ruch_x + gracz.size >= 590:
            if 170 <= gracz.y <= 230 and pozycja_pokoju[0] < 4:
                zmien_pokoj("prawo")
                ruch_x = 0
            else:
                ruch_x = 590 - gracz.size - gracz.x

        if gracz.y + ruch_y - gracz.size <= 10:
            if 270 <= gracz.x <= 330 and pozycja_pokoju[1] > 0:
                zmien_pokoj("gora")
                ruch_y = 0
            else:
                ruch_y = 10 + gracz.size - gracz.y
        elif gracz.y + ruch_y + gracz.size >= 390:
            if 270 <= gracz.x <= 330 and pozycja_pokoju[1] < 4:
                zmien_pokoj("dol")
                ruch_y = 0
            else:
                ruch_y = 390 - gracz.size - gracz.y

        gracz.move(ruch_x, ruch_y)

    if lklatek % 100 == 0 and lokacja.zrespieni_wrogowie < 10:
        ile_zrespic = min(random.randint(1, 3), 10 - lokacja.zrespieni_wrogowie)
        for _ in range(ile_zrespic):
            lokacja.enemies.append(Entity(canvas, 40, 40, 5, "red", 10))
        lokacja.zrespieni_wrogowie += ile_zrespic

    czas_trwania_ms = (time.perf_counter() - czas_startu) * 1000
    opoznienie = max(1, int(30 - czas_trwania_ms))
    okno.after(opoznienie, game_loop)


pokaz_menu()
okno.mainloop()