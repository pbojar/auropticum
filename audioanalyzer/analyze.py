from pathlib import Path
import scipy
import numpy as np
import matplotlib.pyplot as plt

import librosa


def load_from_path(path: Path, sample_rate: int):
    try:
        y, sr = librosa.load(path, sr=sample_rate)
        return y, sr
    except Exception as e:
        raise Exception(f"Error: Could load from path {path}\n\n{e}")

def get_dynamic_beats(y, sr, hop=512):
    tempo_dynamic = librosa.feature.tempo(y=y, sr=sr, aggregate=None, std_bpm=2, hop_length=hop)
    _, beats = librosa.beat.beat_track(y=y, bpm=tempo_dynamic, hop_length=hop, units='time', trim=False)
    return beats

def calc_chroma(y, sr, hop=512):
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop, bins_per_octave=24)
    nn_filter = librosa.decompose.nn_filter(chroma, aggregate=np.median, metric='cosine')
    chroma_filter = np.minimum(chroma, nn_filter)
    chroma_smooth = scipy.ndimage.median_filter(chroma_filter, size=(1, 9))
    return chroma_smooth

def normalize(data, a, b):
    d_min = np.min(data)
    d_max = np.max(data)
    return (b - a) * (data - d_min) / (d_max - d_min) + a

def run_checks(path: Path, frame_rate: int, sample_rate: int):
    if sample_rate % frame_rate:
        raise Exception("Error: sample_rate must be an integer multiple of frame_rate")
    hop = sample_rate // frame_rate
    y_fr, _ = load_from_path(path, frame_rate)
    y_fr_h, y_fr_p = librosa.effects.hpss(y_fr, margin=8, n_fft=1024)
    norm_harm = normalize(y_fr_h, -1, 1)
    norm_perc = normalize(y_fr_p, -1, 1)
    # y, _ = load_from_path(path, sample_rate)
    # y_harm, y_perc = librosa.effects.hpss(y, margin=8)
    # beats = get_dynamic_beats(y_perc, sample_rate, hop)
    # chroma = calc_chroma(y_harm, sample_rate, hop)
    # stft = librosa.stft(y, hop_length=hop)
    return norm_harm, norm_perc
