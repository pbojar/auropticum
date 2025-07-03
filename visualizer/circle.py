import pyglet
import math

class Circle(pyglet.shapes.Arc):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update(self, y):
        self.radius = y
