from tkinter import PhotoImage

class Sprite:
    def __init__(self, pos, size=None, image=None, color=(255, 0, 0)):
        """
        pos: (x, y)
        size: (w, h) optional
        image: PhotoImage (Tkinter)
        color: fill color if no image
        """
        self.pos = pos
        self.x, self.y = pos
        self.image = image
        self.color = color

        if image is not None:
            self.width = image.width()
            self.height = image.height()
        elif size is not None:
            self.width, self.height = size
        else:
            raise ValueError("Sprite needs either 'size' or 'image'")

    # === CLASS METHODS ===
    @classmethod
    def image(cls, img, pos):
        """Create sprite using a Tkinter PhotoImage"""
        return cls(pos, image=img)

    @classmethod
    def rect(cls, pos, w, h, color=(255, 0, 0)):
        """Create sprite using a plain colored rectangle"""
        return cls(pos, size=(w, h), color=color)

    # === METHODS ===
    def draw(self, win):
        """Draw sprite on a CrystalWindow or Tkinter canvas"""
        if self.image:
            win.canvas.create_image(self.x, self.y, anchor="nw", image=self.image)
        else:
            win.draw_rect(self.color, (self.x, self.y, self.width, self.height))

    def move(self, dx, dy):
        """Move sprite by dx/dy"""
        self.x += dx
        self.y += dy
        self.pos = (self.x, self.y)
