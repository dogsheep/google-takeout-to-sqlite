import json
import hashlib
import datetime


def save_my_activity(db, zf):
    my_activities = [
        f.filename for f in zf.filelist if f.filename.endswith("My Activity.json")
    ]
    created = "my_activity" not in db.table_names()
    for filename in my_activities:
        db["my_activity"].upsert_all(
            json.load(zf.open(filename)),
            hash_id="id",
            alter=True,
            column_order=("id", "time", "header", "title"),
        )
    if created:
        db["my_activity"].create_index(["time"])
        db["my_activity"].enable_fts(["title"])


def save_location_history(db, zf):
    location_history = json.load(
        zf.open("Takeout/Location History/Location History.json")
    )
    db["location_history"].upsert_all(
        (
            {
                "id": id_for_location_history(row),
                "latitude": row["latitudeE7"] / 1e7,
                "longitude": row["longitudeE7"] / 1e7,
                "accuracy": row["accuracy"],
                "timestampMs": int(row["timestampMs"]),
                "when": datetime.datetime.utcfromtimestamp(
                    int(row["timestampMs"]) / 1000
                ).isoformat(),
            }
            for row in location_history["locations"]
        ),
        pk="id",
    )


def id_for_location_history(row):
    # We want an ID that is unique but can be sorted by in
    # date order - so we use the isoformat date + the first
    # 6 characters of a hash of the JSON
    first_six = hashlib.sha1(
        json.dumps(row, separators=(",", ":"), sort_keys=True).encode("utf8")
    ).hexdigest()[:6]
    return "{}-{}".format(
        datetime.datetime.utcfromtimestamp(int(row["timestampMs"]) / 1000).isoformat(),
        first_six,
    )
