import json
import hashlib
import datetime
import email
import mailbox
import traceback
from rich.progress import track
from email.utils import parsedate_tz, mktime_tz


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


def get_mbox(mbox_file):
    num_errors = 0
    print("Preparing to process emails...")
    mbox = mailbox.mbox(mbox_file)
    print("Processing {} emails".format(len(mbox)))

    # These are all the Gmail email fields available
    # ['X-GM-THRID', 'X-Gmail-Labels', 'Delivered-To', 'Received', 'Received',
    # 'Return-Path', 'Received', 'Received-SPF', 'Authentication-Results',
    # 'Received', 'Mailing-List', 'Precedence', 'List-Post', 'List-Help',
    # 'List-Unsubscribe', 'List-Subscribe', 'Delivered-To', 'Received',
    # 'Message-ID', 'Date', 'From', 'To', 'MIME-Version', 'Content-Type',
    # 'Content-Transfer-Encoding', 'X-Nabble-From', 'X-pstn-neptune',
    # 'X-pstn-levels', 'X-pstn-settings', 'X-pstn-addresses', 'Subject']

    for email in track(mbox):
        try:
            message = {}
            message["Message-Id"] = email["Message-Id"]
            message["X-GM-THRID"] = email["X-GM-THRID"]
            message["X-Gmail-Labels"] = email["X-Gmail-Labels"]

            # These following try/excepts are here because for some reason
            # these items returned from the mbox module are sometimes strings
            # and sometimes headers and sometimes None.

            try:
                email["From"].decode("utf-8")
            except AttributeError:
                message["From"] = str(email["From"])
            try:
                email["To"].decode("utf-8")
            except AttributeError:
                message["To"] = str(email["To"])

            try:
                email["Subject"].decode("utf-8")
            except AttributeError:
                message["Subject"] = str(email["Subject"])

            message["date"] = get_message_date(email.get("Date"), email.get_from())
            message["body"] = get_email_body(email)

            yield message
        except (TypeError, ValueError, AttributeError, LookupError) as e:
            # How does this project want to handle logging? For now we're just
            # printing out variables
            num_errors = num_errors + 1
            print("Errors: {}".format(num_errors))
            print(traceback.format_exc())
            continue


def save_emails(db, mbox_file):
    """
    Import Gmail mbox from google takeout
    """
    db["mbox_emails"].upsert_all(
        (
            {
                "id": message["Message-Id"],
                "X-GM-THRID": message["X-GM-THRID"],
                "X-Gmail-Labels": message["X-Gmail-Labels"],
                "From": message["From"],
                "To": message["To"],
                "Subject": message["Subject"],
                "when": message["date"],
                "body": message["body"],
            }
            for message in get_mbox(mbox_file)
        ),
        pk="id",
        alter=True,
    )
    print("Finished loading emails into {}.".format(mbox_file))
    print('Enabling full text search on "body" and "Subject" fields')
    db["mbox_emails"].enable_fts(["body", "Subject"])
    print("Finished!")


def get_email_body(message):
    """
    return the email body contents
    """
    body = None
    if message.is_multipart():
        for part in message.walk():
            if part.is_multipart():
                for subpart in part.walk():
                    if subpart.get_content_type() == "text/plain":
                        body = subpart.get_payload(decode=True)
            elif part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)
    elif message.get_content_type() == "text/plain":
        body = message.get_payload(decode=True)
    return body


def get_message_date(get_date, get_from):
    if get_date:
        mail_date = get_date
    else:
        mail_date = get_from.strip()[-30:]

    datetime_tuple = email.utils.parsedate_tz(mail_date)
    if datetime_tuple:
        unix_time = email.utils.mktime_tz(datetime_tuple)
        mail_date_iso8601 = datetime.datetime.utcfromtimestamp(unix_time).isoformat(" ")
    else:
        mail_date_iso8601 = ""

    return mail_date_iso8601
