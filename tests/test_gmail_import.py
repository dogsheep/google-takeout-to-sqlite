from google_takeout_to_sqlite.utils import save_emails
import pathlib
import sqlite_utils


def test_import_gmails():
    path = pathlib.Path(__file__).parent / "mbox_contents/small.gmail.mbox"
    db = sqlite_utils.Database(memory=True)
    save_emails(db, path)
    assert "mbox_emails" in set(db.table_names())
    mbox_emails = list(sorted(db["mbox_emails"].rows, key=lambda r: r["id"]))
    assert [
        {
            "id": "1529555944956622147",
            "when": "2016-03-23 01:57:00",
            "From": "Person Person <Person.Person@example.net>",
            "body": "Nothing worse than being without good wifi\r\n\r\n",
            "Subject": None,
            "To": None,
            "X-GM-THRID": "1529553825574740118",
            "X-Gmail-Labels": "Chat",
        },
        {
            "Subject": "test",
            "From": "罗 <123@example.net>",
            "To": "Person Person <Person.Person@example.net>",
            "id": "1705761119401391280",
            "body": "好好学习，天天向上\r\n",
            "when": "2021-07-20 00:22:49",
            "X-GM-THRID": "1705761119401391280",
            "X-Gmail-Labels": "Chat",
        },
        {
            "From": "Keld Jørn Simonsen <keld@dkuug.dk>",
            "Subject": "[fw-general] Zend_Form and generating fields",
            "To": "fw-general@lists.zend.com",
            "X-GM-THRID": "1277085061787347926",
            "X-Gmail-Labels": "Unread",
            "body": "\r\nUnfortunately it is slow! For 10 products it takes 0.6 sec. to"
            " generate.\r\nIs there a better (more efficient) method to build s"
            "uch forms via Zend_Form?\r\n\r\nThe same I noticed when tried to"
            " create a select element which contained\r\nmany options (i.e. lis"
            "t of countries). Without ajax (autocomplete) it takes\r\nages to g"
            "enerate and seems to be useless in this case. Shame.\r\n\r\nI wo"
            "nder if Zend_Form can be used when it comes to generate a lot of"
            "\r\ninputs/options in select or I`m forced to create it by han"
            "d?\r\n\r\n\r\n\r\n",
            "id": "<18826312.post@talk.nabble.com>",
            "when": "2008-08-05 08:00:12",
        },
        {
            "From": "Person Person <Person.Person@example.net>",
            "Subject": "Re: [Gnumed-devel] Tree view formatting",
            "To": "gnumed-devel@gnu.org",
            "X-GM-THRID": "1278204036336346264",
            "X-Gmail-Labels": "Unread",
            "body": "On Sun, Aug 17, 2008 at 03:09:55PM -0300, Bob Luz wrote:\r\n\r\n"
            "> when you say you have changed it ... can I assume it will make"
            " the 0.3.0 release\r\nyes\r\n\r\n> or is the release READY\r\nI "
            'hope it is "ready" so I can release it within the next few\r\ndays'
            ". I usually wait a few days to see whether any errors\r\nshow up. "
            "That's why we need you guys to test like mad.\r\n\r\n> and all o"
            "ur future discussions on this list\r\n> will from now on to be imp"
            "lemented on the 0.3.1 ?\r\n\r\nNot quite yet. And, rather 0.3+.\r"
            "\n\r\nPerson\r\n\r\n\r\n_________________________________________"
            "______\r\nGnumed-devel mailing list\r\nGnumed-devel@gnu.org\r\nhtt"
            "p://lists.gnu.org/mailman/listinfo/gnumed-devel\r\n",
            "id": "<20080817183915.GM3992@merkur.person.loc>",
            "when": "2008-08-17 18:39:15",
        },
    ] == mbox_emails
