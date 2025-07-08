
from pathlib import Path
import numpy as np

import pyglet
from pyglet.window import key, FPSDisplay

from visualizer import gui, resources
from visualizer.appstates import AppStates
from visualizer.mediaplayer import Player
from audioanalyzer.analyze import run_analysis, normalize
from config import WINDOW_HEIGHT, WINDOW_WIDTH, FRAME_RATE, SAMPLE_RATE


class VisualizerWindow(pyglet.window.Window):

    def __init__(self, show_fps: bool = False, output_images: bool = False):
        super().__init__(
            width=WINDOW_WIDTH, height=WINDOW_HEIGHT, 
            caption='Auropticum', vsync=False
        )
        self.output_images = output_images
        self.out_frame = 0
        self.updated = False
        # Initialize at main menu
        self.app_state = AppStates.MAIN_MENU
        # Frame and sample rate
        self.frame_rate = FRAME_RATE
        self.sample_rate = SAMPLE_RATE
        # FPS display
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
        self.song_over = False
        self.play_batch = pyglet.graphics.Batch()
        self.play_group = self.red_and_white(self.play_batch)
        # Create pause menu
        self.pause_menu_batch = pyglet.graphics.Batch()
        self.pause_menu = self.create_pause_menu(self.pause_menu_batch)
        # Create key handler
        self.key_handler = key.KeyStateHandler()
        self.push_handlers(self.key_handler)
        # Create player
        self.audio_path: Path
        # No need for custom on_player_eos or audio if outputting images
        if self.output_images:
            self.player = pyglet.media.Player()
            self.player.volume = 0
        else:
            self.player = Player(self)
        

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
            font_size=52,
            batch=batch
        )
    
    def red_and_white(self, batch: pyglet.graphics.Batch):
        r_circle = pyglet.shapes.Arc(self.width//2, self.height//2, 100, color=(255, 50, 50), batch=batch)
        w_circle = pyglet.shapes.Arc(self.width//2, self.height//2, 100, color=(255, 255, 255), batch=batch)
        bc_pos = pyglet.shapes.BezierCurve((0, 0), (1, 1), batch=batch)
        bc_neg = pyglet.shapes.BezierCurve((0, 0), (1, 1), batch=batch)
        return [r_circle, w_circle, bc_pos, bc_neg]

    def create_pause_menu(self, batch: pyglet.graphics.Batch):
        menu_texts = ["play", "main menu", "exit"]
        pause_menu = gui.create_menu_labels(menu_texts, self.width//2, self.height//2,
                                            'center', 'bottom', 60, batch)
        return pause_menu

    def on_draw(self):
        self.clear()

        if self.app_state == AppStates.MAIN_MENU:
            self.main_menu_batch.draw()

        if self.app_state == AppStates.ANALYZING:
            self.analysis_batch.draw()
            self.analysis_screen_drawn = True

        if self.app_state == AppStates.PLAYING:
            self.play_batch.draw()
            # if self.output_images and self.updated:
            #     fname = f'images/{self.audio_path.stem}/{self.out_frame}.png'
            #     pyglet.image.get_buffer_manager().get_color_buffer().save(fname)
            #     self.out_frame += 1
            #     self.updated = False

        if self.app_state == AppStates.PAUSED:
            self.pause_menu_batch.draw()

        if self.show_fps:
            self.fps_display.draw()

    def update(self, dt):
        if self.app_state == AppStates.ANALYZING and self.analysis_screen_drawn:
            results = run_analysis(self.audio_path, self.frame_rate, self.sample_rate)
            self.harmonic = list(map(float, results["harmonic"]))
            self.percussive = list(map(float, results["percussive"]))
            # Beats in seconds (np.float) converted to int frames
            self.beats = list(map(int, results["beats"] * self.frame_rate))
            # Scale stft_mag by half of window height and calc corresponding x points
            self.mag_pos_points = []
            self.mag_neg_points = []
            num_pts = 100
            mirror_idx = num_pts//2
            pts_x = [self.width/num_pts * i for i in range(0, num_pts + 1)]
            for row in results["stft_mag"].T:
                scaled = normalize(row[:mirror_idx+1], self.height//2, self.height)
                pts_y = np.concat((scaled[::-1], scaled[1:]))
                pos_points = zip(pts_x, map(float, pts_y))
                neg_points = zip(pts_x, map(float, self.height - pts_y))
                self.mag_pos_points.append(list(pos_points))
                self.mag_neg_points.append(list(neg_points))
            if self.output_images:
                out_path = Path(f'images/{self.audio_path.stem}')
                if not out_path.exists() or not out_path.is_dir():
                    out_path.mkdir(parents=True)
            self.app_state = AppStates.PLAYING
            self.player.play()

        if self.app_state == AppStates.PLAYING:
            # if self.output_images:
            #     self.updated = True
            #     frame = self.out_frame
            # else:
            frame = int(self.player.time * self.frame_rate)
            try:
                self.play_group[0].radius = 100 + 450 * self.percussive[frame]
                self.play_group[1].radius = 200 + 450 * self.harmonic[frame]
                self.play_group[2].points = self.mag_pos_points[frame]
                self.play_group[3].points = self.mag_neg_points[frame]
            except IndexError:
                self.analysis_screen_drawn = False
                self.player.next_source()
                self.app_state = AppStates.MAIN_MENU

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
                pyglet.app.exit()

        if self.app_state in [AppStates.MAIN_MENU, AppStates.PAUSED]:
            if self.app_state == AppStates.MAIN_MENU:
                menu = self.main_menu
                menu_name = 'main'
            elif self.app_state == AppStates.PAUSED:
                menu = self.pause_menu
                menu_name = 'pause'

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
                self.player.play()

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
        elif menu_name == 'pause':
            if item == 'exit':
                pyglet.app.exit()
            elif item == 'play':
                self.app_state = AppStates.PLAYING
                self.player.play()
            elif item == 'main menu':
                self.analysis_screen_drawn = False
                self.player.next_source()
                self.app_state = AppStates.MAIN_MENU
            