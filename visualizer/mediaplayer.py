import pyglet

from visualizer.appstates import AppStates


class Player(pyglet.media.Player):
    """pyglet.media.Player with custom on_player_eos method. 
    
    Custom method is used to reset the app state to the main 
    menu after end of sound file is reached.

    Attributes:
        visWin (VisualizerWindow): pyglet Window for the app.
    """

    def __init__(self, visWin):
        super().__init__()
        self.visWin = visWin

    def on_player_eos(self):
        self.visWin.analysis_screen_drawn = False
        self.next_source()
        self.visWin.app_state = AppStates.MAIN_MENU
