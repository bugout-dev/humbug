"""
This is an example script which shows how to collect error reports in a Bugout.dev knowledge base
using the Humbug Python library.
"""
import sys
import uuid

from humbug.consent import HumbugConsent, environment_variable_opt_out, no
from humbug.report import Reporter

DEMO_BUGOUT_ACCESS_TOKEN = "a390de7a-c64f-482c-b3f4-b9322ffaadef"
DEMO_BUGOUT_JOURNAL_ID = "1bf50549-a8ef-430f-b788-fb2ac864d42a"

"""
LEND ME YOUR EYES, FRIEND:
Please replace the bugout_access_token and bugout_journal_id with the values you generate in the
process of setting up a "Usage Reports" integration at https://bugout.dev.

Full instructions can be found here: https://github.com/bugout-dev/humbug/blob/main/README.md

You can run this script without making the change, but you will not be able to see the changes
under your own Bugout.dev account.

If you would like access to the demo knowledge base, email me at neeraj@bugout.dev.
"""
bugout_access_token: str = DEMO_BUGOUT_ACCESS_TOKEN
bugout_journal_id: str = DEMO_BUGOUT_JOURNAL_ID

if (
    bugout_access_token == DEMO_BUGOUT_ACCESS_TOKEN
    or bugout_journal_id == DEMO_BUGOUT_JOURNAL_ID
):
    print(
        "It seems you are running this script with the demo Bugout access token and journal id."
    )
    print(
        "If you continue, this script will publish reports to a Bugout.dev knowledge base that you do not have access to."
    )
    print(
        "You can always request access by sending an email to Neeraj (neeraj@bugout.dev) with your Bugout.dev username."
    )
    confirm = input("Continue? [Y/n]")
    if confirm.lower() == "n":
        print("Okay, exiting")
        sys.exit(1)

"""
This script uses a consent flow in which consent is granted to report errors by default but users
can opt out of reporting by setting an environment variable:
BUGOUT_DEMO_REPORTING_ENABLED=0

To learn more about consent mechanisms available in the Humbug Python library, read the consent
section in:
https://github.com/bugout-dev/humbug/blob/main/python/README.md
"""
consent = HumbugConsent(
    environment_variable_opt_out("BUGOUT_DEMO_REPORTING_ENABLED", no)
)

"""
Now we create a Humbug reporter object to send reports.
"""
session_id = str(uuid.uuid4())
reporter = Reporter(
    "recipes/error_reporting",
    consent,
    session_id=session_id,
    bugout_token=bugout_access_token,
    bugout_journal_id=bugout_journal_id,
)

"""
There are a few ways to report errors from a Python program. If you are writing your own exception
classes, you can handle reporting in their `__init__` methods as follows:
"""


class Boom(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        reporter.error_report(self)


"""
You can also handle all uncaught exceptions using the sys.excepthook
"""


original_excepthook = sys.excepthook


def humbug_hook(exception_type, exception_instance, traceback):
    reporter.error_report(exception_instance)
    original_excepthook(exception_type, exception_instance, traceback)


sys.excepthook = humbug_hook

if __name__ == "__main__":
    try:
        raise Boom("OH NOES!!!1111")
    except:
        pass

    raise Exception("OH NOES FOR REAL!!1111")
