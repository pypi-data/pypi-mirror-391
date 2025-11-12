import math, tkinter as tk

class CW3D:
    def __init__(self, win):
        self.canvas = win.canvas
        self.angle_x = 0
        self.angle_y = 0
        self.zoom = 200
        self.objects = []

    def project(self, x, y, z):
        """Simple 3D → 2D projection"""
        scale = self.zoom / (z + 4)
        px = self.canvas.winfo_width()/2 + x * scale
        py = self.canvas.winfo_height()/2 + y * scale
        return px, py

    def rotate_point(self, x, y, z):
        """Rotate around X/Y axes"""
        y2 = y * math.cos(self.angle_x) - z * math.sin(self.angle_x)
        z2 = y * math.sin(self.angle_x) + z * math.cos(self.angle_x)
        x2 = x * math.cos(self.angle_y) + z2 * math.sin(self.angle_y)
        z3 = -x * math.sin(self.angle_y) + z2 * math.cos(self.angle_y)
        return x2, y2, z3

    def add_cube(self, size=1, color="cyan"):
        """Add a simple cube"""
        s = size
        points = [
            [-s, -s, -s], [s, -s, -s],
            [s,  s, -s], [-s,  s, -s],
            [-s, -s,  s], [s, -s,  s],
            [s,  s,  s], [-s,  s,  s],
        ]
        edges = [
            (0,1),(1,2),(2,3),(3,0),
            (4,5),(5,6),(6,7),(7,4),
            (0,4),(1,5),(2,6),(3,7)
        ]
        self.objects.append(("cube", points, edges, color))

    def draw(self):
        """Draw all objects"""
        self.canvas.delete("all")
        for obj in self.objects:
            _, pts, edges, color = obj
            rotated = [self.rotate_point(*p) for p in pts]
            for a, b in edges:
                x1, y1 = self.project(*rotated[a])
                x2, y2 = self.project(*rotated[b])
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2)

    def spin(self, ax=0.02, ay=0.03):
        self.angle_x += ax
        self.angle_y += ay

    def run(self):
        """Auto loop"""
        self.draw()
        self.spin()
        self.canvas.after(16, self.run)
