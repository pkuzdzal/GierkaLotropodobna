
class Entity:
    def __init__(self, canvas, x, y, size, color, hp, luck, nazwa="Wróg"):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.canvas = canvas
        self.hp = hp
        self.max_hp = hp
        self.nazwa = nazwa
        self.ekwipunek = []
        self.luck = luck
        self.id = canvas.create_rectangle(
            x - size, y - size, x + size, y + size, fill=color
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

    def utworz_grafike(self):
        self.id = self.canvas.create_rectangle(
            self.x - self.size,
            self.y - self.size,
            self.x + self.size,
            self.y + self.size,
            fill=self.color
        )