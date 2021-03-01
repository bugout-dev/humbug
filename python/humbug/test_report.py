import unittest

from . import consent, report


class TestReporter(unittest.TestCase):
    def setUp(self):
        self.consent = consent.HumbugConsent(True)
        self.reporter = report.Reporter("TestReporter", self.consent)

    def test_system_report_successful(self):
        self.reporter.system_report(publish=False)

    def test_error_report_successful(self):
        error = Exception("This exception is for use in a Humbug Python test")
        self.reporter.error_report(error, publish=False)


if __name__ == "__main__":
    unittest.main()
