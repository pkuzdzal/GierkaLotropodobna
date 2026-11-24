
class Apteczka:
    def __init__(self, canvas, x, y, leczenie=20, size=6, nazwa="Apteczka"):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.leczenie = leczenie
        self.size = size
        self.nazwa = nazwa
        self.id = canvas.create_oval(
            x - size, y - size, x + size, y + size,
            fill="lime", outline="white"
        )

    def ustaw_pozycje(self, x, y):
        self.x = x
        self.y = y
        self.canvas.coords(self.id, x - self.size, y - self.size, x + self.size, y + self.size)

    def podnies(self, gracz):
        gracz.hp = min(gracz.max_hp, gracz.hp + self.leczenie)
        self.canvas.delete(self.id)

    def utworz_grafike(self):
        self.id = self.canvas.create_oval(
            self.x - self.size,
            self.y - self.size,
            self.x + self.size,
            self.y + self.size,
            fill="lime",
            outline="white"
        )