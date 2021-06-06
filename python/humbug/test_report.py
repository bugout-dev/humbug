import unittest

from . import consent, report


class TestReporter(unittest.TestCase):
    def setUp(self):
        self.consent = consent.HumbugConsent(True)
        self.reporter = report.HumbugReporter(
            name="TestReporter", consent=self.consent, tags=["humbug-unit-test"]
        )

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
            set(self.reporter.system_tags() + tags + ["d", "e", "type:system"]),
        )

    def test_env_report_successful(self):
        tags = ["a", "b", "c"]
        env_report = self.reporter.env_report(tags=tags, publish=False)
        self.assertSetEqual(set(env_report.tags), set(tags + ["type:env"]))

    def test_packages_report_successful(self):
        tags = ["a", "b", "c"]
        pkg_report = self.reporter.packages_report(tags=tags, publish=False)
        self.assertSetEqual(set(pkg_report.tags), set(tags + ["type:dependencies"]))

    def test_post_body(self):
        report_title = "xylophone"
        report_content = "xylophones are awesome"
        report_tags = ["music", "instruments"]
        sample_report = report.Report(
            title=report_title, content=report_content, tags=report_tags
        )
        self.assertDictEqual(
            self.reporter._post_body(sample_report),
            {
                "title": report_title,
                "content": report_content,
                "tags": report_tags + self.reporter.tags,
            },
        )


if __name__ == "__main__":
    unittest.main()
