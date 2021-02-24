import os
import unittest

from . import consent


class TestFlypaperConsent(unittest.TestCase):
    def setUp(self):
        os.environ["FLYPAPER_TEST_OPT_IN_AFFIRMATIVE"] = "1"
        os.environ["FLYPAPER_TEST_OPT_OUT_AFFIRMATIVE"] = "1"
        os.environ["FLYPAPER_TEST_OPT_IN_NEGATIVE"] = "0"
        os.environ["FLYPAPER_TEST_OPT_OUT_NEGATIVE"] = "0"
        self.ev_in_not_set = os.environ.get("FLYPAPER_TEST_OPT_IN_NOT_SET")
        if self.ev_in_not_set is not None:
            del os.environ["FLYPAPER_TEST_OPT_IN_NOT_SET"]
        self.ev_out_not_set = os.environ.get("FLYPAPER_TEST_OPT_OUT_NOT_SET")
        if self.ev_out_not_set is not None:
            del os.environ["FLYPAPER_TEST_OPT_OUT_NOT_SET"]

    def tearDown(self) -> None:
        del os.environ["FLYPAPER_TEST_OPT_IN_AFFIRMATIVE"]
        del os.environ["FLYPAPER_TEST_OPT_OUT_AFFIRMATIVE"]
        del os.environ["FLYPAPER_TEST_OPT_IN_NEGATIVE"]
        del os.environ["FLYPAPER_TEST_OPT_OUT_NEGATIVE"]
        if self.ev_in_not_set is not None:
            os.environ["FLYPAPER_TEST_OPT_IN_NOT_SET"] = self.ev_in_not_set
        if self.ev_out_not_set is not None:
            os.environ["FLYPAPER_TEST_OPT_OUT_NOT_SET"] = self.ev_out_not_set

    def test_base_consent_affirmative(self):
        consent_state = consent.FlypaperConsent(True)
        self.assertTrue(consent_state.check())

    def test_base_consent_negative(self):
        consent_state = consent.FlypaperConsent(False)
        self.assertFalse(consent_state.check())

    def test_dynamic_consent_envvar_opt_in_affirmative(self):
        consent_state = consent.FlypaperConsent(
            True,
            consent.environment_variable_opt_in(
                "FLYPAPER_TEST_OPT_IN_AFFIRMATIVE", ["true", "1"]
            ),
        )
        self.assertTrue(consent_state.check())

    def test_dynamic_consent_envvar_opt_in_negative(self):
        consent_state = consent.FlypaperConsent(
            True,
            consent.environment_variable_opt_in(
                "FLYPAPER_TEST_OPT_IN_NEGATIVE", ["true", "1"]
            ),
        )
        self.assertFalse(consent_state.check())

    def test_dynamic_consent_envvar_opt_in_not_set(self):
        consent_state = consent.FlypaperConsent(
            True,
            consent.environment_variable_opt_in(
                "FLYPAPER_TEST_OPT_IN_NOT_SET", ["true", "1"]
            ),
        )
        self.assertFalse(consent_state.check())

    def test_dynamic_consent_envvar_opt_out_affirmative(self):
        consent_state = consent.FlypaperConsent(
            True,
            consent.environment_variable_opt_out(
                "FLYPAPER_TEST_OPT_OUT_AFFIRMATIVE", ["true", "1"]
            ),
        )
        self.assertFalse(consent_state.check())

    def test_dynamic_consent_envvar_opt_out_negative(self):
        consent_state = consent.FlypaperConsent(
            True,
            consent.environment_variable_opt_out(
                "FLYPAPER_TEST_OPT_OUT_NEGATIVE", ["true", "1"]
            ),
        )
        self.assertTrue(consent_state.check())

    def test_dynamic_consent_envvar_opt_out_not_set(self):
        consent_state = consent.FlypaperConsent(
            True,
            consent.environment_variable_opt_out(
                "FLYPAPER_TEST_OPT_OUT_NOT_SET", ["true", "1"]
            ),
        )
        self.assertTrue(consent_state.check())

    def test_dynamic_consent_all_allow(self):
        consent_state = consent.FlypaperConsent(
            True,
            consent.environment_variable_opt_in(
                "FLYPAPER_TEST_OPT_IN_AFFIRMATIVE", ["1"]
            ),
            consent.environment_variable_opt_out(
                "FLYPAPER_TEST_OPT_OUT_NEGATIVE", ["1"]
            ),
        )
        self.assertTrue(consent_state.check())

    def test_dynamic_consent_middle_reject_opt_in_var(self):
        consent_state = consent.FlypaperConsent(
            True,
            consent.environment_variable_opt_in("FLYPAPER_TEST_OPT_IN_NEGATIVE", ["1"]),
            consent.environment_variable_opt_out(
                "FLYPAPER_TEST_OPT_OUT_NEGATIVE", ["1"]
            ),
        )
        self.assertFalse(consent_state.check())

    def test_dynamic_consent_middle_reject_opt_out_var(self):
        consent_state = consent.FlypaperConsent(
            True,
            consent.environment_variable_opt_in(
                "FLYPAPER_TEST_OPT_IN_AFFIRMATIVE", ["1"]
            ),
            consent.environment_variable_opt_out(
                "FLYPAPER_TEST_OPT_OUT_AFFIRMATIVE", ["1"]
            ),
        )
        self.assertFalse(consent_state.check())


if __name__ == "__main__":
    unittest.main()
