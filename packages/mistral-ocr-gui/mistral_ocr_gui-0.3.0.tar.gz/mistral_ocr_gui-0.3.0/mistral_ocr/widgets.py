# mistral_ocr/widgets.py
"""
Contains custom Tkinter widgets for the Mistral OCR GUI application.
"""

import tkinter as tk

class ProgressBarGrid(tk.Frame):
    """
    A custom widget to display progress as a grid of colored squares.
    """
    SQUARE_SIZE = 12
    PADDING = 2

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg='white', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        self.square_ids = []
        self.square_colors = []
        
        self.canvas.bind("<Configure>", self._on_resize)
    
    def setup_grid(self, num_items):
        """Initializes or resets the grid with a specific number of items."""
        self.clear()
        self.square_ids = [None] * num_items
        self.square_colors = ['#FFFFFF'] * num_items # Use hex for white
        for i in range(num_items):
            self.square_ids[i] = self.canvas.create_rectangle(0, 0, 0, 0, outline='black', fill='#FFFFFF', width=1)
        self.after(10, self._redraw_squares) # Delay to ensure canvas is sized

    def update_square(self, index, color):
        """Updates the color of a specific square in the grid."""
        if 0 <= index < len(self.square_ids):
            self.square_colors[index] = color
            item_id = self.square_ids[index]
            if item_id:
                self.canvas.itemconfig(item_id, fill=color)

    def clear(self):
        """Clears all squares from the canvas."""
        self.canvas.delete("all")
        self.square_ids = []
        self.square_colors = []

    def _on_resize(self, event=None):
        """Handles the canvas resize event to redraw the grid."""
        self._redraw_squares()

    def _redraw_squares(self):
        """Recalculates positions and redraws all squares based on canvas size."""
        if not self.square_ids:
            return

        canvas_width = self.canvas.winfo_width()
        if canvas_width < self.SQUARE_SIZE:
            return

        total_square_width = self.SQUARE_SIZE + self.PADDING
        cols = max(1, canvas_width // total_square_width)
        
        x, y = self.PADDING, self.PADDING
        
        for i, item_id in enumerate(self.square_ids):
            if i > 0 and i % cols == 0:
                x = self.PADDING
                y += self.SQUARE_SIZE + self.PADDING

            x0, y0 = x, y
            x1, y1 = x + self.SQUARE_SIZE, y + self.SQUARE_SIZE
            
            self.canvas.coords(item_id, x0, y0, x1, y1)
            self.canvas.itemconfig(item_id, fill=self.square_colors[i])
            
            x += self.SQUARE_SIZE + self.PADDING