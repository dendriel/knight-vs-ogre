"""Small immutable-ish UI helpers shared by every screen (T05): a vertical menu and a row of clickable cards.
No pygame import needed: drawing goes through View.text()/View.panel(), mouse positions arrive already converted to the
internal 480x270 canvas."""


class Rect:
    def __init__(self, x, y, w, h): self.x, self.y, self.w, self.h = x, y, w, h
    def contains(self, p): return self.x <= p[0] < self.x + self.w and self.y <= p[1] < self.y + self.h
    def tuple(self): return (self.x, self.y, self.w, self.h)


class Menu:
    """Vertical list of entries [(label, action, enabled)]: UP/DOWN + Enter, or hover + click."""
    def __init__(self, items, x, y, w=150, row_h=20):
        self.items = items; self.index = 0; self.x, self.y, self.w, self.row_h = x, y, w, row_h
        self.hover = None

    def rect(self, i): return Rect(self.x, self.y + i * self.row_h, self.w, self.row_h - 3)

    def move(self, d):
        n = len(self.items)
        for _ in range(n):                                 # skip disabled entries
            self.index = (self.index + d) % n
            if self.items[self.index][2]: break

    def mouse_move(self, pos):
        for i in range(len(self.items)):
            if self.rect(i).contains(pos):
                self.hover = i
                if self.items[i][2]: self.index = i
                return
        self.hover = None

    def click(self, pos):
        """Returns the action of the clicked entry (or None)."""
        for i, (label, action, enabled) in enumerate(self.items):
            if enabled and self.rect(i).contains(pos): self.index = i; return action
        return None

    def current(self):
        label, action, enabled = self.items[self.index]
        return action if enabled else None
