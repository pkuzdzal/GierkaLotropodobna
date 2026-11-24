class Sciana:
    def __init__(self, canvas, x1, y1, x2, y2):
        self.canvas = canvas
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)
        self.id = canvas.create_rectangle(
            self.x1, self.y1, self.x2, self.y2,
            fill="#555555", outline="#888888", width=2
        )

    def usun(self):
        self.canvas.delete(self.id)

    def koliduje(self, x, y, margines=0):
        return (
            x + margines > self.x1 and x - margines < self.x2 and
            y + margines > self.y1 and y - margines < self.y2
        )
