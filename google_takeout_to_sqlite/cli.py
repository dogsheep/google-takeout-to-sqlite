import click
import os
import sqlite_utils
import json
from google_takeout_to_sqlite import utils
import sqlite_utils
import zipfile


@click.group()
@click.version_option()
def cli():
    "Save data from Google Takeout to a SQLite database"


@cli.command(name="my-activity")
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.argument(
    "zip_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
def my_activity(db_path, zip_path):
    "Import all My Activity data from Takeout zip to SQLite"
    db = sqlite_utils.Database(db_path)
    zf = zipfile.ZipFile(zip_path)
    utils.save_my_activity(db, zf)


@cli.command(name="location-history")
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.argument(
    "zip_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
def my_activity(db_path, zip_path):
    "Import all Location History data from Takeout zip to SQLite"
    db = sqlite_utils.Database(db_path)
    zf = zipfile.ZipFile(zip_path)
    utils.save_location_history(db, zf)
