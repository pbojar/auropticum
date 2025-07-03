from enum import Enum
from pathlib import Path

import pyglet
from pyglet.window import key, FPSDisplay

from visualizer import gui, resources
from visualizer.circle import Circle
from audioanalyzer.analyze import run_checks


class AppStates(Enum):
    MAIN_MENU = 0
    ANALYZING = 1
    PLAYING = 2
    PAUSED = 3


class VisualizerWindow(pyglet.window.Window):

    def __init__(self, show_fps: bool = False):
        super().__init__(width=1920, height=1080, caption='Auropticum', 
                         resizable=True, vsync=False)
        # Initialize at main menu
        self.app_state = AppStates.MAIN_MENU
        # FPS display
        self.frame_rate = 90 # Targeting 90 FPS
        self.fps_display = FPSDisplay(self)
        self.show_fps = show_fps
        # Create main menu
        self.main_menu_batch = pyglet.graphics.Batch()
        self.audio_paths = resources.get_audio_paths()
        self.main_menu_title, self.main_menu = self.create_main_menu(self.main_menu_batch)
        # Create analysis screen
        self.analysis_screen_drawn = False
        self.harmonic: list[float]
        self.percussive: list[float]
        self.analysis_batch = pyglet.graphics.Batch()
        self.analysis_screen: pyglet.text.Label
        # Create play screen
        self.frame = 0
        self.play_batch = pyglet.graphics.Batch()
        # TODO: More interesting visual effects
        self.play_group = self.red_and_white(self.play_batch)
        # TODO: Add pause menu [continue, change song, exit]
        # Create key handler
        self.key_handler = key.KeyStateHandler()
        self.push_handlers(self.key_handler)
        # Create player
        self.audio_path: Path
        self.player = pyglet.media.Player()

        pyglet.clock.schedule_interval(self.update, 1.0 / self.frame_rate)

    def create_main_menu(self, batch: pyglet.graphics.Batch):
        main_menu_title = pyglet.text.Label(
            text="Auropticum",
            x=20, y=3*self.height//4,
            anchor_x='left', anchor_y='bottom',
            font_size=62,
            batch=batch
        )
        menu_texts = list(self.audio_paths.keys()) + ['exit']
        main_menu = gui.create_menu_labels(menu_texts, 60, 3*self.height//4, 
                                           'left', 'top', 60, batch)
        return main_menu_title, main_menu
    
    def create_analysis_screen(self, batch: pyglet.graphics.Batch):
        return pyglet.text.Label(
            text=f"Analyzing {self.audio_path.stem}...",
            x=self.width//2, y=self.height//2,
            anchor_x='center', anchor_y='center',
            font_size=62,
            batch=batch
        )
    
    def red_and_white(self, batch: pyglet.graphics.Batch):
        r_circle = Circle(self.width//2, self.height//2, 100, color=(180, 50, 50), batch=batch)
        w_circle = Circle(self.width//2, self.height//2, 100, color=(255, 255, 255), batch=batch)
        return [r_circle, w_circle]

    def on_draw(self):
        self.clear()

        if self.app_state == AppStates.MAIN_MENU:
            self.main_menu_batch.draw()

        if self.app_state == AppStates.ANALYZING:
            self.analysis_batch.draw()
            self.analysis_screen_drawn = True

        if self.app_state == AppStates.PLAYING:
            self.play_batch.draw()

        if self.show_fps:
            self.fps_display.draw()

    def update(self, dt):
        if self.app_state == AppStates.ANALYZING and self.analysis_screen_drawn:
            self.harmonic, self.percussive = run_checks(self.audio_path, self.frame_rate, 22050)
            self.harmonic = list(map(float, self.harmonic))
            self.percussive = list(map(float, self.percussive))
            self.app_state = AppStates.PLAYING

        if self.app_state == AppStates.PLAYING:
            self.play_group[0].update(100 + 450 * self.percussive[self.frame])
            self.play_group[1].update(200 + 450 * self.harmonic[self.frame])
            if not self.player.playing:
                self.player.play()
            self.frame += 1

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
                pyglet.app.exit()

        if self.app_state in [AppStates.MAIN_MENU]:
            if self.app_state == AppStates.MAIN_MENU:
                menu = self.main_menu
                menu_name = 'main'

            if symbol == key.DOWN:
                self.move_menu_select(menu, 1)
            elif symbol == key.UP:
                self.move_menu_select(menu, -1)
            elif symbol == key.ENTER:
                self.handle_menu_press(
                    self.selected_menu_text(menu), menu_name)

        if self.app_state == AppStates.PLAYING:
            if symbol == key.SPACE:
                self.app_state = AppStates.PAUSED
                self.player.pause()
        elif self.app_state == AppStates.PAUSED:
            if symbol == key.SPACE:
                self.app_state = AppStates.PLAYING

    def move_menu_select(self, menu, index):
        """ moves the selected menu item by index amount of items """
        prev_selected_index = 0
        for i in range(len(menu)):
            if menu[i].color[3] == 255:
                prev_selected_index = i

        menu[prev_selected_index].color = (255, 255, 255, 76)
        menu[(prev_selected_index+index)%len(menu)].color = \
            (255, 255, 255, 255)
        
    def selected_menu_text(self, menu):
        """ Get's the selected menu item's text """

        selected_index = 0
        for i in range(len(menu)):
            if menu[i].color[3] == 255:
                selected_index = i

        return menu[selected_index].text
    
    def handle_menu_press(self, item, menu_name):
        """ Handles selection in menus """

        if menu_name == 'main':
            if item == 'exit':
                pyglet.app.exit()
            else:
                self.audio_path = self.audio_paths[item]
                source = pyglet.media.load(str(self.audio_path))
                self.player.queue(source)
                self.analysis_screen = self.create_analysis_screen(self.analysis_batch)
                self.app_state = AppStates.ANALYZING
            