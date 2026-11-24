import tkinter as tk
from tkinter import simpledialog, messagebox
import time
import random
from Entity import Entity
from Mapa import Mapa
from Przedmioty.Apteczka import Apteczka
from Przedmioty.ObszarObrazen import ObszarObrazen
from Wall import Sciana

global immunity_frames

okno = tk.Tk(baseName="Gra Lotropodobna")
okno.title("Gra Lotropodobna")
okno.geometry("600x400")
okno.resizable(False, False)
okno.configure(background="black")

canvas = tk.Canvas(okno, width=600, height=400, bg="grey")
canvas.pack()

gracz = None
current_level = None
hp_text_id = None
klawisze = {}
swiat = {}
pozycja_pokoju = (2, 2)
predkosc = 5
lklatek = 0
gra_aktywna = False
pauza = False
lprzeciwikow = 0
immunity_frames=0


def pytaj_xy(tytul):
    odp = simpledialog.askstring(tytul, "Podaj współrzędne x,y (np. 200,150):", parent=okno)
    if not odp:
        return None
    try:
        x, y = map(int, odp.split(","))
        return x, y
    except ValueError:
        messagebox.showerror("Błąd", "Zły format! Wpisz np. 200,150")
        return None


def otworz_menu_testowe():
    global pauza
    if current_level is None:
        messagebox.showinfo("Info", "Najpierw kliknij NOWA GRA.")
        return

    if pauza:
        return

    pauza = True
    klawisze.clear()

    panel = tk.Toplevel(okno)
    panel.title("Testy (T)")
    panel.geometry("260x390")
    panel.resizable(False, False)

    def zamknij():
        global pauza
        pauza = False
        panel.destroy()

    panel.protocol("WM_DELETE_WINDOW", zamknij)

    def btn(tekst, akcja):
        tk.Button(panel, text=tekst, command=akcja).pack(fill=tk.X, padx=10, pady=3)

    def dodaj_sciane():
        odp = simpledialog.askstring("Ściana", "Podaj x1,y1,x2,y2 (np. 150,100,250,120):", parent=panel)
        if odp:
            try:
                x1, y1, x2, y2 = map(int, odp.split(","))
                if not current_level.dodaj_sciane(x1, y1, x2, y2):
                    messagebox.showwarning("Błąd", "Nie można postawić tu ściany.")
            except ValueError:
                messagebox.showerror("Błąd", "Wpisz 4 liczby oddzielone przecinkami.")

    def dodaj_wroga():
        wsp = pytaj_xy("Dodaj wroga")
        if wsp and not current_level.umiesc_istote(Entity(canvas, wsp[0], wsp[1], 5, "red", 10, luck=1), *wsp):
            messagebox.showwarning("Błąd", "Pole zajęte lub ściana.")

    def usun_wroga():
        wsp = pytaj_xy("Usuń wroga")
        if wsp and not current_level.usun_istote(*wsp):
            messagebox.showinfo("Info", "Brak wroga w tym miejscu.")

    def dodaj_przedmiot():
        wsp = pytaj_xy("Dodaj apteczkę")
        if wsp and not current_level.umiesc_przedmiot(Apteczka(canvas, wsp[0], wsp[1]), *wsp):
            messagebox.showwarning("Błąd", "Pole zajęte lub ściana.")

    def usun_przedmiot():
        wsp = pytaj_xy("Usuń przedmiot")
        if wsp and not current_level.usun_przedmiot(*wsp):
            messagebox.showinfo("Info", "Brak przedmiotu w tym miejscu.")

    def przesun_gracza():
        wsp = pytaj_xy("Przenieś gracza")
        if wsp:
            if current_level.czy_mozna_umiescic_istote(wsp[0], wsp[1], gracz.size):
                gracz.ustaw_pozycje(*wsp)
            else:
                messagebox.showwarning("Błąd", "Gracz nie może tam stanąć.")
    
    def usun_sciane():
        wsp=pytaj_xy("Usun sciane")
        if wsp and not current_level.usun_sciane(*wsp):
            messagebox.showwarning("Błąd", "Pole bez sciany.")
    
    def wczytaj_plik():
        global current_level
        try:
            current_level.wyczysc()
            current_level = Mapa.z_pliku("mapa.txt", canvas, hp_text_id)
            messagebox.showinfo("OK", "Wczytano z mapa.txt")
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    btn("Dodaj ścianę (x1,y1,x2,y2)", dodaj_sciane)
    btn("Usuń ścianę (x1, y1)", usun_sciane)
    btn("Dodaj wroga (x,y)", dodaj_wroga)
    btn("Usuń wroga (x,y)", usun_wroga)
    btn("Dodaj apteczkę (x,y)", dodaj_przedmiot)
    btn("Usuń przedmiot (x,y)", usun_przedmiot)
    btn("Przenieś gracza (x,y)", przesun_gracza)
    btn("Wyczyść mapę (pusta)", current_level.wyczysc)
    btn("Zapisz do mapa.txt", lambda: (current_level.zapisz_do_pliku("mapa.txt"), messagebox.showinfo("OK", "Zapisano do mapa.txt")))
    btn("Wczytaj z mapa.txt", wczytaj_plik)
    btn("Pokaż raport obiektów", lambda: messagebox.showinfo("Raport mapy", current_level.raport(gracz)))



def pokaz_menu():
    canvas.delete("all")
    canvas.create_rectangle(10, 10, 590, 390, fill="black")
    canvas.create_text(300, 140, text="GRA LOTROPODOBNA", fill="white", font=("Arial", 22, "bold"))
    btn_start = tk.Button(okno, text="NOWA GRA", font=("Arial", 14, "bold"), command=start_gry)
    canvas.create_window(300, 220, window=btn_start)

def zmien_pokoj(kierunek):
    global current_level, pozycja_pokoju, lklatek
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

    current_level.ukryj_zawartosc()
    pozycja_pokoju = nowe_wsp
    gracz.ustaw_pozycje(nowy_x, nowy_y)
    lklatek = 0

    if pozycja_pokoju not in swiat:
        swiat[pozycja_pokoju] = Mapa(canvas, pozycja_pokoju[0], pozycja_pokoju[1], hp_text_id, gracz)
        current_level = swiat[pozycja_pokoju]
        current_level.rysuj_wyjscia()
    else:
        current_level = swiat[pozycja_pokoju]
        current_level.pokaz_zawartosc()


def start_gry():
    global gracz, current_level, hp_text_id, lklatek, gra_aktywna, pauza
    canvas.delete("all")
    canvas.create_rectangle(10, 10, 590, 390, fill="black")

    klawisze.clear()
    lklatek = 0
    gra_aktywna = True
    pauza = False

    gracz = Entity(canvas, x=300, y=200, size=10, color="blue", hp=100, luck=0.1 , nazwa="Gracz")
    gracz.dodaj_przedmiot(ObszarObrazen(canvas, gracz, promien=50))

    hp_text_id = canvas.create_text(50, 30, fill="lightblue", text=f"HP: {gracz.hp}", font=("Arial", 12, "bold"))
    current_level = Mapa(canvas, 2, 2, hp_text_id, gracz)
    current_level.rysuj_wyjscia()
    game_loop()


def koniec_gry(kolor_tekstu):
    global gra_aktywna
    gra_aktywna = False
    canvas.create_text(300, 180, text="KONIEC GRY", fill=kolor_tekstu, font=("Arial", 24, "bold"))
    okno.after(2000, pokaz_menu)


def nacisniecie(event):
    klawisz = event.keysym.lower()
    if klawisz == "t":
        otworz_menu_testowe()
        return
    klawisze[klawisz] = True


def puszczenie(event):
    klawisze[event.keysym.lower()] = False


okno.bind("<KeyPress>", nacisniecie)
okno.bind("<KeyRelease>", puszczenie)


def game_loop():
    global lklatek
    if not gra_aktywna:
        return

    czas_startu = time.perf_counter()
    lklatek += 1
    if immunity_frames>0:
        immunity_frames-=1

    current_level.check_collision(gracz, immunity_frames)
    current_level.move_enemies(gracz)
    gracz.uzyj_przedmiotow(current_level.enemies)

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

        current_level.przesun_ze_scianami(gracz, ruch_x, ruch_y)

    if lklatek % 100 == 0 and current_level.zrespieni_wrogowie < 10:
        ile_zrespic = min(random.randint(1, 3), 10 - current_level.zrespieni_wrogowie)
        for _ in range(ile_zrespic):
            current_level.enemies.append(Entity(canvas, 40, 40, 5, "red", 10, luck=1))
        current_level.zrespieni_wrogowie += ile_zrespic

    czas_trwania_ms = (time.perf_counter() - czas_startu) * 1000
    opoznienie = max(1, int(30 - czas_trwania_ms))
    okno.after(opoznienie, game_loop)


pokaz_menu()
okno.mainloop()