import pathlib
from .utils import create_zip


def test_create_zip():
    zf = create_zip()
    assert {
        "Takeout/My Activity/Maps/My Activity.json",
        "Takeout/My Activity/Search/My Activity.json",
        "Takeout/My Activity/Google Play Books/My Activity.json",
        "Takeout/Location History/Location History.json",
    } == {f.filename for f in zf.filelist}
