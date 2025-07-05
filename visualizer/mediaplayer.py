import pyglet

from visualizer.appstates import AppStates


class Player(pyglet.media.Player):

    def __init__(self, visWin):
        super().__init__()
        self.visWin = visWin

    def on_player_eos(self):
        self.visWin.analysis_screen_drawn = False
        self.next_source()
        self.visWin.app_state = AppStates.MAIN_MENU
