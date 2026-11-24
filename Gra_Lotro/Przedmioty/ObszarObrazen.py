import random

class ObszarObrazen:
    def __init__(self, canvas, wlasciciel, promien=50, dps=20 / 3):
        self.canvas = canvas
        self.wlasciciel = wlasciciel
        self.promien = promien
        self.obrazenia_na_klatke = dps * 0.05
        self.id = canvas.create_oval(
            wlasciciel.x - promien, wlasciciel.y - promien,
            wlasciciel.x + promien, wlasciciel.y + promien,
            outline="cyan", width=2
        )
        self.canvas.tag_lower(self.id, wlasciciel.id)

    def aktualizuj_pozycje(self):
        self.canvas.coords(
            self.id,
            self.wlasciciel.x - self.promien, self.wlasciciel.y - self.promien,
            self.wlasciciel.x + self.promien, self.wlasciciel.y + self.promien
        )

    def uzyj(self, enemies):
        for wrog in enemies[:]:
            dystans = ((wrog.x - self.wlasciciel.x) ** 2 + (wrog.y - self.wlasciciel.y) ** 2) ** 0.5
            if dystans <= self.promien + wrog.size:

                min_dmg = self.obrazenia_na_klatke*self.wlasciciel.luck
                max_dmg = self.obrazenia_na_klatke
                dmg_now = random.uniform(min_dmg, max_dmg)

                wrog.hp -= dmg_now
                if wrog.hp <= 0:
                    self.canvas.delete(wrog.id)
                    enemies.remove(wrog)

                linie = []
                linie.append(f"Gracz zadaje {dmg_now} wrogowi w {int(wrog.x)}; {int(wrog.y)}")
                with open("logi.txt", "a", encoding="utf-8") as plik:
                    plik.write("\n".join(linie) + "\n")