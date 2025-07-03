import pyglet

from visualizer.visualize import VisualizerWindow


if __name__ == '__main__':

    main_window = VisualizerWindow(show_fps=True)
    pyglet.app.run()
