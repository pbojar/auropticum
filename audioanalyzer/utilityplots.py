from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

import librosa


def plot_beats_from_dir(media_dir: Path):
    if not media_dir.exists() or not media_dir.is_dir():
        raise Exception(f"Error: {media_dir} does not exist or is not a directory!")
    for file in media_dir.iterdir():
        if file.suffix not in ['.mp3', '.wav']:
            continue
        y, sr = librosa.load(file, duration=30, offset=30)
        onsenv_4, beats_4 = get_dynamic_beats(y, sr, 12)
        onsenv_8, beats_8 = get_dynamic_beats(y, sr, 16)
        plot_beats(sr, onsenv_4, beats_4, onsenv_8, beats_8, file.stem)
   
def get_dynamic_beats(y, sr, margin):
    y_perc = librosa.effects.percussive(y=y, margin=margin)
    onset_env = librosa.onset.onset_strength(y=y_perc, sr=sr)
    tempo_dynamic = librosa.feature.tempo(y=y_perc, sr=sr, aggregate=None, std_bpm=1.5)
    _, beats = librosa.beat.beat_track(onset_envelope=onset_env, bpm=tempo_dynamic)
    return onset_env, beats

def plot_beats(sr, onset_env_0, beats_0, onset_env_1, beats_1, name):
    fig, ax = plt.subplots(nrows=2, sharex=True, sharey=True)

    times_0 = librosa.times_like(onset_env_0, sr=sr)
    ax[0].plot(times_0, librosa.util.normalize(onset_env_0), 
               label='Onset strength')
    ax[0].vlines(times_0[beats_0], 0, 1, alpha=0.5, color='r', 
                 linestyle='--', label='Beats 0')
    ax[0].legend()
    ax[0].set(title='Beats 0')
    ax[0].label_outer()

    times_1 = librosa.times_like(onset_env_1, sr=sr)
    ax[1].plot(times_1, librosa.util.normalize(onset_env_1),
               label='Onset strength')
    ax[1].vlines(times_1[beats_1], 0, 1, alpha=0.5, color='r',
                 linestyle='--', label='Beats 1')
    ax[1].legend()
    ax[1].set(title='Beats 1')
    ax[1].xaxis.set_major_formatter(librosa.display.TimeFormatter())

    fig.savefig(f"beats__{name}.png")

def plot_hpss_specs_from_dir(media_dir: Path):
    if not media_dir.exists() or not media_dir.is_dir():
        raise Exception(f"Error: {media_dir} does not exist or is not a directory!")
    for file in media_dir.iterdir():
        if file.suffix not in ['.mp3', '.wav']:
            continue
        y, sr = librosa.load(file, duration=30)
        D = librosa.stft(y)
        for margin in [1, 2, 4, 8]:
            plot_hpss_spectrograms(D, margin, file.stem)

def plot_hpss_spectrograms(D, margin, name):

    rp = np.max(np.abs(D))
    D_harmonic, D_percussive = librosa.decompose.hpss(D, margin=margin)

    fig, ax = plt.subplots(nrows=3, sharex=True, sharey=True)
    img = librosa.display.specshow(librosa.amplitude_to_db(np.abs(D), ref=rp),
                         y_axis='log', x_axis='time', ax=ax[0])
    ax[0].set(title='Full spectrogram')
    ax[0].label_outer()

    librosa.display.specshow(librosa.amplitude_to_db(np.abs(D_harmonic), ref=rp),
                            y_axis='log', x_axis='time', ax=ax[1])
    ax[1].set(title='Harmonic spectrogram')
    ax[1].label_outer()

    librosa.display.specshow(librosa.amplitude_to_db(np.abs(D_percussive), ref=rp),
                            y_axis='log', x_axis='time', ax=ax[2])
    ax[2].set(title='Percussive spectrogram')
    fig.colorbar(img, ax=ax)

    fig.savefig(f"hpss-spec-m{margin}__{name}.png")
