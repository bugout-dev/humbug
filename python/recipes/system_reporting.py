"""
This is an example script which shows how to collect error reports in a Bugout.dev knowledge base
using the Humbug Python library.
"""
import sys
import uuid

from humbug.consent import HumbugConsent, environment_variable_opt_out, no
from humbug.report import HumbugReporter

DEMO_BUGOUT_ACCESS_TOKEN = "a390de7a-c64f-482c-b3f4-b9322ffaadef"

"""
LEND ME YOUR EYES, FRIEND:
Please replace the bugout_access_token with the value you generate in the
process of setting up a "Usage Reports" integration at https://bugout.dev.

Full instructions can be found here: https://github.com/bugout-dev/humbug/blob/main/README.md

You can run this script without making the change, but you will not be able to see the changes
under your own Bugout.dev account.

If you would like access to the demo knowledge base, email me at neeraj@bugout.dev.
"""
bugout_access_token: str = DEMO_BUGOUT_ACCESS_TOKEN

if bugout_access_token == DEMO_BUGOUT_ACCESS_TOKEN:
    print("It seems you are running this script with the demo Bugout access token.")
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
This script uses a consent flow in which consent is granted by default but users can opt out of
reporting by setting an environment variable:
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
reporter = HumbugReporter(
    name="recipes/system_reporting",
    consent=consent,
    session_id=session_id,
    bugout_token=bugout_access_token,
)

"""
This script simply sends a system report to your Bugout.dev knowledge base, with helpful information
like Python version, OS, etc.

By default, all reports are sent in the background.
"""

reporter.system_report()


def main():
    """
    In your own code, this function would probably do something non-trivial. :)
    """
    print("Hello")
    print("and goodbye!")


if __name__ == "__main__":
    main()
