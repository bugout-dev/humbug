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

    def test_custom_report_successful(self):
        title = "a"
        tags = ["b", "c", "d"]
        content = "e"
        report = self.reporter.custom_report(title, content, tags, publish=False)
        self.assertEqual(report.title, title)
        self.assertListEqual(report.tags, tags)
        self.assertEqual(report.content, content)

    def test_compound_report_successful(self):
        title = "a"
        tags = ["b", "c", "d"]
        content = "e"
        system_report = self.reporter.system_report(publish=False)
        custom_report = self.reporter.custom_report(title, content, tags, publish=False)
        title = "lol"
        compound_report = self.reporter.compound_report(
            [system_report, custom_report], title=title, tags=["d", "e"], publish=False
        )
        self.assertEqual(compound_report.title, title)
        self.assertSetEqual(
            set(compound_report.tags),
            set(self.reporter.system_tags() + tags + ["d", "e"]),
        )

    def test_env_report_successful(self):
        tags = ["a", "b", "c"]
        env_report = self.reporter.env_report(tags=tags, publish=False)
        self.assertListEqual(env_report.tags, tags)

    def test_packages_report_successful(self):
        tags = ["a", "b", "c"]
        pkg_report = self.reporter.packages_report(tags=tags, publish=False)
        self.assertListEqual(pkg_report.tags, tags)


if __name__ == "__main__":
    unittest.main()
