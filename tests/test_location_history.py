from google_takeout_to_sqlite.utils import save_location_history
import pathlib
import sqlite_utils
from .utils import create_zip


def test_location_history():
    path = pathlib.Path(__file__).parent / "zip_contents"
    zf = create_zip(path)
    db = sqlite_utils.Database(memory=True)
    save_location_history(db, zf)
    assert {"location_history"} == set(db.table_names())
    location_history = list(sorted(db["location_history"].rows, key=lambda r: r["id"]))
    assert [
        {
            "id": "2015-07-18T23:57:26.012000-bc0cdf",
            "latitude": 37.6955289,
            "longitude": -121.9287261,
            "accuracy": 45,
            "timestampMs": 1437263846012,
            "when": "2015-07-18T23:57:26.012000",
        },
        {
            "id": "2015-07-18T23:58:25.529000-138e18",
            "latitude": 37.6955454,
            "longitude": -121.9287454,
            "accuracy": 43,
            "timestampMs": 1437263905529,
            "when": "2015-07-18T23:58:25.529000",
        },
    ] == location_history
