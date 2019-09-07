import zipfile
import pathlib
import io


def create_zip(path=None):
    path = path or pathlib.Path(__file__).parent / "zip_contents"
    zf = zipfile.ZipFile(io.BytesIO(), "w")
    for filepath in path.glob("**/*"):
        if filepath.is_file():
            zf.write(filepath, str(filepath.relative_to(path)))
    return zf
