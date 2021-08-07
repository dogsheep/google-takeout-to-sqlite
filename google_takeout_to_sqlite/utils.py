import json
import hashlib
import datetime
import email
from email import policy, header
import traceback
import re

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

def parse_mbox(mbox_file):
    with open(mbox_file, 'rb') as f:
        delivery_date = ''
        message_id = ''
        lines = []

        while True:
            line = f.readline()

            is_new_record = line.startswith(b'From ')
            is_eof = len(line) == 0

            if is_eof or is_new_record:
                message = b''.join(lines)
                if message:
                    yield delivery_date, message_id, email.message_from_bytes(message, policy=policy.compat32)
            else:
                lines.append(line)

            if is_new_record:
                (message_id, delivery_date) = re.match(r'^From (\w+)@xxx (.+)\r\n', line.decode('utf-8')).groups()
                lines = []
            elif is_eof:
                break

def get_mbox(mbox_file):
    num_errors = 0

    # These are all the Gmail email fields available
    # ['X-GM-THRID', 'X-Gmail-Labels', 'Delivered-To', 'Received', 'Received',
    # 'Return-Path', 'Received', 'Received-SPF', 'Authentication-Results',
    # 'Received', 'Mailing-List', 'Precedence', 'List-Post', 'List-Help',
    # 'List-Unsubscribe', 'List-Subscribe', 'Delivered-To', 'Received',
    # 'Message-ID', 'Date', 'From', 'To', 'MIME-Version', 'Content-Type',
    # 'Content-Transfer-Encoding', 'X-Nabble-From', 'X-pstn-neptune',
    # 'X-pstn-levels', 'X-pstn-settings', 'X-pstn-addresses', 'Subject']

    for delivery_date, gmail_message_id, email in parse_mbox(mbox_file):
        try:
            message = {}
            message["Message-Id"] = email["Message-Id"]
            if message["Message-Id"] is None:
                message["Message-Id"] = gmail_message_id
            message["X-GM-THRID"] = email["X-GM-THRID"]
            message["X-Gmail-Labels"] = email["X-Gmail-Labels"]

            message["From"] = get_email_header(email, "From")
            message["To"] = get_email_header(email, "To")
            message["Subject"] = get_email_header(email, "Subject")

            if "Date" in email:
                message["date"] = parse_mail_date(email["Date"])
            else:
                message["date"] = parse_mail_date(delivery_date)

            body = get_email_body(email)
            try:
                message["body"] = body.decode('utf-8')
            except UnicodeDecodeError:
                message["body"] = body
            except AttributeError:
                message["body"] = body

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
                "id": message["Message-Id"] if "Message-Id" in message else message["X-GM-THRID"],
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

def get_email_header(message, name, failobj=None):
    # get will either return a str, email.header.Header, or None.
    # This function converts the Header to a str if one is returned.
    value = message.get(name)
    if value is None:
        return failobj
    else:
        try:
            return decode_rfc_2047_str(value)
        except:
            # If the value is invalid, return the un-decoded string.
            return value

def decode_rfc_2047_str(value):
    parts = []

    for part, enc in header.decode_header(value):
        try:
            part = part.decode(enc or 'utf-8')
        except LookupError: # encoding not found
            part = part.decode('utf-8')
        except AttributeError: # part was already a str
            pass

        parts.append(part)

    return ''.join(parts)

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


def parse_mail_date(mail_date):
    datetime_tuple = email.utils.parsedate_tz(mail_date)
    if not datetime_tuple:
        return ""

    unix_time = email.utils.mktime_tz(datetime_tuple)
    mail_date_iso8601 = datetime.datetime.utcfromtimestamp(unix_time).isoformat(" ")
    return mail_date_iso8601
