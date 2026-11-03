import tkinter as tk
import time
import sys

class Entity:
    def __init__(self, canvas, x, y, size, color):
        self.x=x
        self.y=y
        self.size=size
        self.color=color
        self.canvas=canvas
        self.id=canvas.create_rectangle(
            self.x-self.size,
            self.y-self.size,
            self.x+self.size,
            self.y+self.size,
            fill=color
        )

    def move(self, dx, dy):
        self.x+=dx
        self.y+=dy

        self.canvas.coords(
            self.id,
            self.x-self.size, self.y-self.size,
            self.x+self.size, self.y+self.size
        )




okno=tk.Tk(baseName="Gra Lotropodobna")
tk.Canvas
okno.title("Gra Lotropodobna")
okno.geometry("600x400")
okno.resizable(False, False)
okno.configure(background="black")
canvas = tk.Canvas(okno, width=600, height=400, bg="black")
canvas.pack()
gracz = Entity(canvas, x=300, y=200, size=5, color="blue")
cwel = Entity(canvas, 40, 40, 15, "red")

klawisze = {}

def nacisniecie(event):
    klawisze[event.keysym] = True

def puszczenie(event):
    klawisze[event.keysym] = False


okno.bind("<KeyPress>", nacisniecie)
okno.bind("<KeyRelease>", puszczenie)

def game_loop():
    predkosc = 5


    if klawisze.get("w") and klawisze.get("d"):
        gracz.move(predkosc*0.75, -predkosc*0.75)
    elif klawisze.get("w") and klawisze.get("a"):
        gracz.move(-predkosc*0.75, -predkosc*0.75)
    elif klawisze.get("s") and klawisze.get("d"):
        gracz.move(predkosc*0.75, predkosc*0.75)
    elif klawisze.get("s") and klawisze.get("a"):
        gracz.move(-predkosc * 0.75, predkosc * 0.75)
    elif klawisze.get("w"):
        gracz.move(0, -predkosc) # w górę (Y maleje)
    elif klawisze.get("s"):
        gracz.move(0, predkosc)  # w dół (Y rośnie)
    elif klawisze.get("a"):
        gracz.move(-predkosc, 0) # w lewo (X maleje)
    elif klawisze.get("d"):
        gracz.move(predkosc, 0)  # w prawo (X rośnie)

    if gracz.x<0 or gracz.x>600 or gracz.y<0 or gracz.y>400:
        canvas.create_text(300, 200, text="KONIEC GRY", fill='blue')
        canvas.update()
        time.sleep(4)
        sys.exit()

    okno.after(30, game_loop)
game_loop()
okno.mainloop()