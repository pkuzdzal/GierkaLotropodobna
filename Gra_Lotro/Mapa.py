import random
from Wall import Sciana
from Entity import Entity
from Przedmioty.Apteczka import Apteczka

import random


class Mapa:
    def __init__(self, canvas, pokoj_x, pokoj_y, hp_text_id, gracz, pusta_mapa=False):
        self.canvas = canvas
        self.pokoj_x = pokoj_x
        self.pokoj_y = pokoj_y
        self.hp_text_id = hp_text_id
        self.sciany = []
        self.enemies = []
        self.przedmioty_na_ziemi = []
        self.zrespieni_wrogowie = 0
        self.wyjscia_id = []

        if not pusta_mapa and gracz:
            self.generuj_sciany(gracz)
            self.zresp_wroga_losowo()
            self.zrespieni_wrogowie = len(self.enemies)
            self.generuj_przedmioty(gracz)

    @classmethod
    def pusta(cls, canvas, pokoj_x, pokoj_y, hp_text_id, zabudowana=False):
        mapa = cls(canvas, pokoj_x, pokoj_y, hp_text_id, None, pusta_mapa=True)
        if zabudowana:
            mapa.sciany.append(Sciana(canvas, 10, 10, 590, 390))
        return mapa

    @classmethod
    def z_pliku(cls, sciezka, canvas, pokoj_x, pokoj_y, hp_text_id):
        mapa = cls.pusta(canvas, pokoj_x, pokoj_y, hp_text_id)
        with open(sciezka, "r", encoding="utf-8") as plik:
            for linia in plik:
                dane = [x.strip() for x in linia.strip().split(";")]
                if not dane[0]:
                    continue
                if dane[0] == "SCIANA":
                    mapa.dodaj_sciane(*map(float, dane[1:5]))
                elif dane[0] == "ISTOTA":
                    x, y, size, hp = map(float, dane[1:5])
                    mapa.umiesc_istote(Entity(canvas, x, y, size, "red", hp), x, y)
                elif dane[0] == "PRZEDMIOT":
                    x, y, leczenie = map(float, dane[1:4])
                    mapa.umiesc_przedmiot(Apteczka(canvas, x, y, leczenie), x, y)
        mapa.zrespieni_wrogowie = len(mapa.enemies)
        return mapa

    def zapisz_do_pliku(self, sciezka):
        linie = []
        for s in self.sciany:
            linie.append(f"SCIANA;{int(s.x1)};{int(s.y1)};{int(s.x2)};{int(s.y2)}")
        for e in self.enemies:
            linie.append(f"ISTOTA;{int(e.x)};{int(e.y)};{int(e.size)};{int(e.hp)}")
        for p in self.przedmioty_na_ziemi:
            linie.append(f"PRZEDMIOT;{int(p.x)};{int(p.y)};{int(p.leczenie)}")
        with open(sciezka, "w", encoding="utf-8") as plik:
            plik.write("\n".join(linie) + "\n")

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

    def generuj_sciany(self, gracz):
        for _ in range(random.randint(4, 6)):
            for _ in range(30):
                w, h = (random.randint(60, 130), 20) if random.choice([True, False]) else (20, random.randint(60, 120))
                x1, y1 = random.randint(50, 550 - w), random.randint(50, 350 - h)
                x2, y2 = x1 + w, y1 + h

                if gracz and x2 > gracz.x - 40 and x1 < gracz.x + 40 and y2 > gracz.y - 40 and y1 < gracz.y + 40:
                    continue

                if x1 < 80 or x2 > 520 or y1 < 80 or y2 > 320:
                    pass

                if self.dodaj_sciane(x1, y1, x2, y2):
                    break

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
        for sciana in self.sciany:
            self.canvas.delete(sciana.id)  #

    def pokaz_zawartosc(self):
        self.rysuj_wyjscia()
        for sciana in self.sciany:
            sciana.id = self.canvas.create_rectangle(
                sciana.x1, sciana.y1, sciana.x2, sciana.y2,
                fill="#555555", outline="#888888", width=2
            )
        for wrog in self.enemies:
            wrog.utworz_grafike()
        for przedmiot in self.przedmioty_na_ziemi:
            przedmiot.utworz_grafike()

    def czy_koliduje_ze_sciana(self, x, y, r):
        return any(s.koliduje(x, y, r) for s in self.sciany)

    def czy_mozna_umiescic_przedmiot(self, x, y, r=6):
        if x - r < 10 or x + r > 590 or y - r < 10 or y + r > 390:
            return False
        if self.czy_koliduje_ze_sciana(x, y, r):
            return False
        return all(((x - p.x) ** 2 + (y - p.y) ** 2) ** 0.5 >= p.size + r + 4 for p in self.przedmioty_na_ziemi)

    def czy_mozna_umiescic_istote(self, x, y, r=5, ignoruj=None):
        if x - r < 10 or x + r > 590 or y - r < 10 or y + r > 390:
            return False
        if self.czy_koliduje_ze_sciana(x, y, r):
            return False
        for e in self.enemies:
            if e is not ignoruj and ((x - e.x) ** 2 + (y - e.y) ** 2) ** 0.5 < e.size + r + 2:
                return False
        return True

    def dodaj_sciane(self, x1, y1, x2, y2):
        sx1, sy1, sx2, sy2 = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
        if sx2 - sx1 < 5 or sy2 - sy1 < 5 or sx1 < 10 or sx2 > 590 or sy1 < 10 or sy2 > 390:
            return None
        sciana = Sciana(self.canvas, sx1, sy1, sx2, sy2)
        self.sciany.append(sciana)
        return sciana

    def umiesc_przedmiot(self, przedmiot, x, y):
        if not self.czy_mozna_umiescic_przedmiot(x, y, przedmiot.size):
            self.canvas.delete(przedmiot.id)
            return False
        przedmiot.ustaw_pozycje(x, y)
        if przedmiot not in self.przedmioty_na_ziemi:
            self.przedmioty_na_ziemi.append(przedmiot)
        return True

    def umiesc_istote(self, istota, x, y):
        if not self.czy_mozna_umiescic_istote(x, y, istota.size, ignoruj=istota):
            self.canvas.delete(istota.id)
            return False
        istota.ustaw_pozycje(x, y)
        if istota not in self.enemies:
            self.enemies.append(istota)
        return True

    def usun_przedmiot(self, x, y):
        for p in self.przedmioty_na_ziemi[:]:
            if ((p.x - x) ** 2 + (p.y - y) ** 2) ** 0.5 <= p.size + 15:
                self.canvas.delete(p.id)
                self.przedmioty_na_ziemi.remove(p)
                return True
        return False

    def usun_istote(self, x, y):
        for e in self.enemies[:]:
            if ((e.x - x) ** 2 + (e.y - y) ** 2) ** 0.5 <= e.size + 15:
                self.canvas.delete(e.id)
                self.enemies.remove(e)
                return True
        return False

    def wyczysc(self):
        for s in self.sciany:
            s.usun()
        for e in self.enemies:
            self.canvas.delete(e.id)
        for p in self.przedmioty_na_ziemi:
            self.canvas.delete(p.id)
        self.sciany.clear()
        self.enemies.clear()
        self.przedmioty_na_ziemi.clear()

    def raport(self, gracz):
        tekst = [f"Ściany ({len(self.sciany)}):"]
        for s in self.sciany:
            tekst.append(f"  ({int(s.x1)}, {int(s.y1)}) -> ({int(s.x2)}, {int(s.y2)})")
        tekst.append(f"\nIstoty ({len(self.enemies) + 1}):")
        if gracz:
            tekst.append(f"  Gracz: ({int(gracz.x)}, {int(gracz.y)}) HP={int(gracz.hp)}")
        for e in self.enemies:
            tekst.append(f"  {e.nazwa}: ({int(e.x)}, {int(e.y)}) HP={round(e.hp, 1)}")
        tekst.append(f"\nPrzedmioty ({len(self.przedmioty_na_ziemi)}):")
        for p in self.przedmioty_na_ziemi:
            tekst.append(f"  {p.nazwa}: ({int(p.x)}, {int(p.y)})")
        return "\n".join(tekst)

    def generuj_sciany(self, gracz):
        for _ in range(random.randint(4, 6)):
            for _ in range(30):
                w, h = (random.randint(60, 130), 20) if random.choice([True, False]) else (20, random.randint(60, 120))
                x1, y1 = random.randint(40, 560 - w), random.randint(40, 360 - h)
                x2, y2 = x1 + w, y1 + h
                if gracz and x2 > gracz.x - 30 and x1 < gracz.x + 30 and y2 > gracz.y - 30 and y1 < gracz.y + 30:
                    continue
                if self.dodaj_sciane(x1, y1, x2, y2):
                    break

    def zresp_wroga_losowo(self):
        for _ in range(40):
            x, y = random.randint(30, 570), random.randint(30, 370)
            if self.czy_mozna_umiescic_istote(x, y, 5):
                wrog = Entity(self.canvas, x, y, 5, "red", 10, luck=1)
                self.umiesc_istote(wrog, x, y)
                return wrog
        return None

    def generuj_przedmioty(self, gracz):
        ile = random.randint(1, 3)
        rozmiar_apteczki = 6
        for _ in range(ile):
            for _ in range(40):
                x, y = random.randint(30, 570), random.randint(30, 370)
                if gracz and ((x - gracz.x) ** 2 + (y - gracz.y) ** 2) ** 0.5 < gracz.size + rozmiar_apteczki + 10:
                    continue
                if self.umiesc_przedmiot(Apteczka(self.canvas, x, y, size=rozmiar_apteczki), x, y):
                    break

    def przesun_ze_scianami(self, obiekt, rx, ry):
        if rx != 0:
            nowy_x = obiekt.x + rx
            if not self.czy_koliduje_ze_sciana(nowy_x, obiekt.y, obiekt.size):
                obiekt.move(rx, 0)

        if ry != 0:
            nowy_y = obiekt.y + ry
            if not self.czy_koliduje_ze_sciana(obiekt.x, nowy_y, obiekt.size):
                obiekt.move(0, ry)

    def move_enemies(self, gracz):
        for i in self.enemies:
            dx, dy = gracz.x - i.x, gracz.y - i.y
            dist = (dx ** 2 + dy ** 2) ** 0.5
            speed = 3
            if dist > speed:
                self.przesun_ze_scianami(i, (dx / dist) * speed, (dy / dist) * speed)
            elif dist > 0:
                self.przesun_ze_scianami(i, dx, dy)

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
                    self.przesun_ze_scianami(e1, push_x, push_y)
                    self.przesun_ze_scianami(e2, -push_x, -push_y)
                elif distance == 0:
                    self.przesun_ze_scianami(e1, 1.5, 0)
                    self.przesun_ze_scianami(e2, -1.5, 0)

    def check_collision(self, gracz, immunity_frames):
        for i in self.enemies:
            if abs(i.x - gracz.x) < 15 and abs(i.y - gracz.y) < 15:
                gracz.hp -= 1
                self.canvas.itemconfig(self.hp_text_id, text=f"HP: {gracz.hp}")
                linie = []
                linie.append(f"Wrog zadaje 1 obrazen graczowi")
                with open("logi.txt", "a", encoding="utf-8") as plik:
                    plik.write("\n".join(linie) + "\n")
                immunity_frames=5
                return immunity_frames


        for p in self.przedmioty_na_ziemi[:]:
            if ((p.x - gracz.x) ** 2 + (p.y - gracz.y) ** 2) ** 0.5 <= gracz.size + p.size:
                p.podnies(gracz)
                self.przedmioty_na_ziemi.remove(p)
                self.canvas.itemconfig(self.hp_text_id, text=f"HP: {gracz.hp}")

    def usun_sciane(self, x, y):
        for s in self.sciany[:]:
            if s.koliduje(x, y, margines=20):
                s.usun()
                self.sciany.remove(s)
                return True
        return False