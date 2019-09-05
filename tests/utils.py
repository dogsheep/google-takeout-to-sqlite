import zipfile
import pathlib
import io


def create_zip(path):
    zf = zipfile.ZipFile(io.BytesIO(), "w")
    for filepath in path.glob("**/*"):
        if filepath.is_file():
            zf.write(filepath)
    return zf
