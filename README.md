# auropticum
A music visualization app written in Python using [pyglet](https://pyglet.readthedocs.io/en/latest/index.html) and [librosa](https://librosa.org/doc/latest/index.html).

## Installation
1. Install [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) for your platform. Conda handles the binary dependencies for librosa more robustly than PyPI.

2. Clone or download the repository.

3. Create a conda environment using `requirements.txt`:

```
$ conda create --name <env> --file <PATH-TO-REPO>/requirements.txt
```

4. Add songs (as `.mp3` or `.wav` files) to the empty `media` directory. Songs must be added before running the app.

5. Activate your conda environment:

```
$ conda activate <env>
```

6. (Optional) Edit `config.py` to change the window size, frame rate, and sample rate.

7. Run `main.py`:

```
$ python .\main.py
```

## Controls
A windoow will pop-up that can be controlled as follows:

- `UP/DOWN` arrow keys for navigating the menus
- `ENTER` to make a selection
- `ESC` to close the app at any time
- `SPACE` to pause/resume the app when it is playing/paused

## Expected Behavior
The app will start in the main menu where the user can select a song from the `media` directory.

Once a song is selected, the app will analyze the sound file. This can take a couple of minutes for long songs. This analysis must only be run once for each combination of song, frame rate, and sample rate. The results are saved in the hidden `audioanalyzer/.analysis-cache` directory to be quickly re-loaded on subsequent runs.

After the analysis, the song will start to play in sync with the generated visuals. The user may pause the app at any time during this phase by pressing `SPACE`. The app will return to the main menu after the song finishes.

Edit `config.py` to change the window size, frame rate, and sample rate.

Here's an example video:

Have fun!
