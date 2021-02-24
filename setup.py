from setuptools import setup
import os

VERSION = "0.2"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="google-takeout-to-sqlite",
    description="Save data from Google Takeout to a SQLite database",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/dogsheep/google-takeout-to-sqlite",
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["google_takeout_to_sqlite"],
    entry_points="""
        [console_scripts]
        google-takeout-to-sqlite=google_takeout_to_sqlite.cli:cli
    """,
    install_requires=["sqlite-utils~=1.11", "rich"],
    extras_require={"test": ["pytest"]},
    tests_require=["google-takeout-to-sqlite[test]"],
)
