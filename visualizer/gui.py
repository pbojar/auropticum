import pyglet
from pyglet.graphics import Batch
from pyglet.text import Label
from pyglet.window import Window


def create_menu_label(text: str, x: int, y: int, anchor_x, anchor_y, 
                      batch: Batch, selected: bool = False) -> Label:
    return pyglet.text.Label(
        text=text,
        x=x, y=y,
        anchor_x=anchor_x,
        anchor_y=anchor_y,
        font_size=36,
        color=(255, 255, 255, 255 if selected else 76),
        batch=batch
    )

def create_menu_labels(texts: list[str], x: int, y_start: int, anchor_x, anchor_y, 
                       y_step: int, batch: Batch) -> list[Label]:
    menu = []
    y = y_start
    for i in range(len(texts)):
        is_selected = i == 0
        menu_item = create_menu_label(texts[i], x, y, anchor_x, anchor_y, batch, is_selected)
        menu.append(menu_item)
        y -= y_step
    return menu
