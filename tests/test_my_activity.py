from google_takeout_to_sqlite.utils import save_my_activity
import pathlib
import sqlite_utils
from .utils import create_zip


def test_my_activity():
    path = pathlib.Path(__file__).parent / "my_activity"
    zf = create_zip(path)
    db = sqlite_utils.Database(memory=True)
    save_my_activity(db, zf)
    assert {
        "my_activity",
        "my_activity_fts",
        "my_activity_fts_data",
        "my_activity_fts_idx",
        "my_activity_fts_docsize",
        "my_activity_fts_config",
    } == set(db.table_names())
    my_activity = list(db["my_activity"].rows)
    assert [
        {
            "id": "e117fe5174d8b0efdcbcef2bc01ca64bbfd54210",
            "time": "2019-05-30T05:17:16.626Z",
            "header": "Maps",
            "title": "Viewed area around Pheba",
            "titleUrl": "https://www.google.com/maps/@33.5067677,-88.9401891,67620.1214991777a,30y",
            "products": '["Maps"]',
            "locationInfos": None,
        },
        {
            "id": "b21b224d850ea6cca542c044eb4de22cf2875013",
            "time": "2019-05-30T05:16:57.708Z",
            "header": "Maps",
            "title": "Searched for Oktibbeha County Lake, Mississippi, USA",
            "titleUrl": "https://www.google.co.uk/maps/place/Oktibbeha+County+Lake/@33.5088281,-88.9432825,14z/data=!3m1!4b1!4m2!3m1!1s0x888139e250271cc3:0x9efde6f03cb09645",
            "products": '["Maps"]',
            "locationInfos": '[{"name": "Around this area", "url": "https://www.google.com/maps/@?api=1&map_action=map&center=37.773692,-122.429737&zoom=13", "source": "From your device"}]',
        },
        {
            "id": "fbf07d31b6482ee9adc11b4ca84521696bad5435",
            "time": "2019-05-30T15:37:18.828Z",
            "header": "Search",
            "title": "Visited data liberation - How to download Google Search history? - Web ...",
            "titleUrl": "https://www.google.com/url?q=https://webapps.stackexchange.com/questions/95560/how-to-download-google-search-history&usg=AFQjCNF1Madwj4UsKA4EP-2mOUHKDYxEKQ",
            "products": '["Search"]',
            "locationInfos": None,
        },
        {
            "id": "0df418b47f249727a91cb232e302465558fe2124",
            "time": "2019-05-30T15:37:14.947Z",
            "header": "Search",
            "title": 'Searched for "myactivity" google export',
            "titleUrl": "https://www.google.com/search?q=%22myactivity%22+google+export",
            "products": '["Search"]',
            "locationInfos": '[{"name": "Around this area", "url": "https://www.google.com/maps/@?api=1&map_action=map&center=37.773692,-122.429737&zoom=13", "source": "From your places (Home)", "sourceUrl": "https://support.google.com/maps/answer/3184808"}]',
        },
        {
            "id": "a0c041356e94b37f88781dea7f00dd79bed39c46",
            "time": "2018-12-08T22:05:47.249Z",
            "header": "Google Play Books",
            "title": "Visited Play Books App",
            "titleUrl": "https://play.google.com/store/books/",
            "products": '["Google Play Books"]',
            "locationInfos": None,
        },
    ] == my_activity
