# google-takeout-to-sqlite

[![PyPI](https://img.shields.io/pypi/v/google-takeout-to-sqlite.svg)](https://pypi.org/project/google-takeout-to-sqlite/)
[![CircleCI](https://circleci.com/gh/dogsheep/google-takeout-to-sqlite.svg?style=svg)](https://circleci.com/gh/dogsheep/google-takeout-to-sqlite)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/dogsheep/google-takeout-to-sqlite/blob/master/LICENSE)

Save data from google-takeout to a SQLite database.

## How to install

    $ pip install google-takeout-to-sqlite

Request your Google data from https://takeout.google.com/

## My Activity

This tool currently only supports the "My Activity" option. Request that and then run the following command:

    $ google-takeout-to-sqlite takeout.db ~/Downloads/takeout-20190530T153901Z-001.zip

This will create a databae file called `takeout.db`.

You can then browse your data using [Datasette](https://github.com/simonw/datasette) like this:

    $ datasette takeout.db