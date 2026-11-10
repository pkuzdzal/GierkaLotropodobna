import tkinter as tk
import time
import sys


class Entity:
    def __init__(self, canvas, x, y, size, color, hp):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.canvas = canvas
        self.hp = hp
        self.id = canvas.create_rectangle(
            self.x - self.size,
            self.y - self.size,
            self.x + self.size,
            self.y + self.size,
            fill=color
        )

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.canvas.coords(
            self.id,
            self.x - self.size, self.y - self.size,
            self.x + self.size, self.y + self.size
        )


class Mapa:
    def __init__(self, canvas, enemies, hp_text_id):
        self.canvas = canvas
        self.enemies = enemies
        self.hp_text_id = hp_text_id

    def MoveEnemies(self, gracz):
        # 1. Move enemies toward the player
        for i in self.enemies:
            dx = i.x - gracz.x
            dy = i.y - gracz.y

            if dx < 0:
                i.move(3, 0)
            else:
                i.move(-3, 0)
            if dy < 0:
                i.move(0, 3)
            else:
                i.move(0, -3)

        # 2. Prevent enemies from stacking on each other
        for i in range(len(self.enemies)):
            for j in range(i + 1, len(self.enemies)):
                e1 = self.enemies[i]
                e2 = self.enemies[j]

                dx = e1.x - e2.x
                dy = e1.y - e2.y
                distance = (dx ** 2 + dy ** 2) ** 0.5
                min_distance = e1.size + e2.size + 4

                if distance < min_distance and distance > 0:
                    push_x = (dx / distance) * 1.5
                    push_y = (dy / distance) * 1.5
                    e1.move(push_x, push_y)
                    e2.move(-push_x, -push_y)

    def CheckCollision(self, gracz):
        for i in self.enemies:
            dx = i.x - gracz.x
            dy = i.y - gracz.y
            if abs(dx) < 15 and abs(dy) < 15:
                gracz.hp -= 1  # Reduced slightly so it doesn't drain instantly at 30fps
                # Update the existing text item instead of creating a new one
                self.canvas.itemconfig(self.hp_text_id, text=f"HP: {gracz.hp}")

    def UpdateEnemies(self, enemies):
        self.enemies = enemies


okno = tk.Tk(baseName="Gra Lotropodobna")
okno.title("Gra Lotropodobna")
okno.geometry("600x400")
okno.resizable(False, False)
okno.configure(background="black")

canvas = tk.Canvas(okno, width=600, height=400, bg="grey")
canvas.create_rectangle(10, 10, 590, 390, fill="black")
canvas.pack()

gracz = Entity(canvas, x=300, y=200, size=10, color="blue", hp=100)
przeciwnik = Entity(canvas, 40, 40, 5, "red", 10)
enemies = [przeciwnik]

# Create the HP text once and save its ID reference
hp_text_id = canvas.create_text(50, 30, fill="lightblue", text=f"HP: {gracz.hp}", font=("Arial", 12, "bold"))

lokacja = Mapa(canvas, enemies, hp_text_id)

klawisze = {}


def nacisniecie(event):
    klawisze[event.keysym] = True


def puszczenie(event):
    klawisze[event.keysym] = False


okno.bind("<KeyPress>", nacisniecie)
okno.bind("<KeyRelease>", puszczenie)

predkosc = 5
lklatek = 0


def game_loop():
    global lklatek
    lklatek += 1

    lokacja.CheckCollision(gracz)
    lokacja.MoveEnemies(gracz)

    # Check if player died from HP loss
    if gracz.hp <= 0:
        canvas.create_text(300, 200, text="KONIEC GRY", fill='red', font=("Arial", 24, "bold"))
        canvas.update()
        time.sleep(3)
        sys.exit()

    if klawisze.get("w") and klawisze.get("d"):
        gracz.move(predkosc * 0.75, -predkosc * 0.75)
    elif klawisze.get("w") and klawisze.get("a"):
        gracz.move(-predkosc * 0.75, -predkosc * 0.75)
    elif klawisze.get("s") and klawisze.get("d"):
        gracz.move(predkosc * 0.75, predkosc * 0.75)
    elif klawisze.get("s") and klawisze.get("a"):
        gracz.move(-predkosc * 0.75, predkosc * 0.75)
    elif klawisze.get("w"):
        gracz.move(0, -predkosc)
    elif klawisze.get("s"):
        gracz.move(0, predkosc)
    elif klawisze.get("a"):
        gracz.move(-predkosc, 0)
    elif klawisze.get("d"):
        gracz.move(predkosc, 0)

    if gracz.x < 0 or gracz.x > 600 or gracz.y < 0 or gracz.y > 400:
        canvas.create_text(300, 200, text="KONIEC GRY", fill='blue', font=("Arial", 24, "bold"))
        canvas.update()
        time.sleep(3)
        sys.exit()

    if lklatek % 100 == 0:
        nowy_przeciwnik = Entity(canvas, 40, 40, 5, "red", 10)
        enemies.append(nowy_przeciwnik)
        lokacja.UpdateEnemies(enemies)

    okno.after(30, game_loop)


game_loop()
okno.mainloop()