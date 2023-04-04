import unittest
from unittest.mock import MagicMock

from . import consent, report, blacklist


class TestReporter(unittest.TestCase):
    def setUp(self):
        self.consent = consent.HumbugConsent(True)
        self.reporter = report.HumbugReporter(
            name="TestReporter",
            consent=self.consent,
            tags=["humbug-unit-test"],
            blacklist_fn=blacklist.generate_filter_parameters_by_key_inner_fn(
                ["private"]
            ),
        )
        self.reporter.publish = MagicMock()

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

        excepted_tags = tags + ["type:dependencies"]

        if not self.reporter.pkg_resources_exists:
            excepted_tags.append("warning:pkg_resources_import_failed")

        self.assertSetEqual(set(pkg_report.tags), set(tags + excepted_tags))

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

    def test_feature_report(self):
        report = self.reporter.feature_report(
            "test_feature",
            {
                "population": "A",
                "version": "2",
                "private": "confidential",
                "inner": {"private": "confidential"},
            },
            publish=False,
        )
        self.assertTrue("feature:{}".format("test_feature") in report.tags)
        self.assertTrue("parameter:{}={}".format("population", "A") in report.tags)
        self.assertTrue("parameter:{}={}".format("version", "2") in report.tags)
        self.assertTrue(
            "parameter:{}={}".format("private", "confidential") not in report.tags
        )
        self.assertTrue("parameter:{}={{}}".format("inner") in report.tags)

    def test_feature_report_not_apply_blacklist(self):
        report = self.reporter.feature_report(
            "test_feature_not_apply_blacklist",
            {
                "private": "confidential",
                "inner": {"private": "confidential"},
            },
            publish=False,
            apply_blacklist=False,
        )
        self.assertTrue(
            "parameter:{}={}".format("private", "confidential") in report.tags
        )
        self.assertTrue("parameter:{}={{}}".format("inner") not in report.tags)

    def test_record_call(self):
        @self.reporter.record_call
        def the_answer(life, universe=None, everything=None):
            return 42

        result = the_answer(1, everything="lol")

        self.assertEqual(result, 42)
        self.reporter.publish.assert_called_once()
        publish_args = self.reporter.publish.call_args
        self.assertIsNotNone(publish_args)
        # Python 3.7 -> Python 3.8 introduced call_args.args.
        # We use the older syntax to ensure compatibility with Python 3.6 and 3.7.
        self.assertEqual(len(publish_args[0]), 1)
        report = publish_args[0][0]
        self.assertTrue("feature:the_answer" in report.tags)
        self.assertTrue("parameter:arg.0=1" in report.tags)
        self.assertTrue("parameter:everything=lol" in report.tags)

    def test_record_errors(self):
        @self.reporter.record_errors
        def broken():
            raise Exception("Go away")

        with self.assertRaises(Exception):
            broken()

        self.reporter.publish.assert_called_once()
        publish_args = self.reporter.publish.call_args
        self.assertIsNotNone(publish_args)
        self.assertEqual(len(publish_args[0]), 1)
        report = publish_args[0][0]
        self.assertTrue("site:broken" in report.tags)

    def test_metrics_report(self):
        tags = ["a", "b", "c"]
        metrics_report = self.reporter.metrics_report(tags=tags, publish=False)
        self.assertSetEqual(set(metrics_report.tags), set(tags + ["type:metrics"]))


if __name__ == "__main__":
    unittest.main()
