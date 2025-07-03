from pathlib import Path

import pyglet


vis_app_path = Path(__file__).parent.absolute()
media_path = vis_app_path.parent.joinpath('media')

pyglet.resource.path.append(str(media_path))
pyglet.resource.reindex()


def get_audio_paths() -> dict[str, Path]:
    """ 
    Get mp3 and wav files in media_path. 
    
    Returns paths - a dict of file_name: file_path.
    """
    paths = {}
    for file in media_path.iterdir():
        if file.suffix in ['.mp3', '.wav']:
            paths[file.stem] = file
    return paths
