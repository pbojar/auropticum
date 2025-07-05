from pathlib import Path
import hashlib
import pickle

archive_dir = Path(__file__).parent.joinpath('.analysis-cache')


def create_hash(str):
    return hashlib.sha256(str)

def search_archive(hash):
    hex_dig = hash.hexdigest()
    archive = archive_dir.joinpath(hex_dig[:6] + hex_dig[-6:])
    if archive.exists() and archive.is_file():
        return archive
    return False

def write_archive(hash, data, overwrite=False):
    hex_dig = hash.hexdigest()
    archive = archive_dir.joinpath(hex_dig[:6] + hex_dig[-6:])
    if archive.exists() and not overwrite:
        raise Exception("Error: Existing archive found!")
    if not archive.parent.exists():
        archive.parent.mkdir()
    with archive.open('wb') as f:
        pickle.dump(data, f)

def read_archive(hash):
    archive = search_archive(hash)
    if archive:
        with archive.open('rb') as f:
            data = pickle.load(f)
        return data
    return False
