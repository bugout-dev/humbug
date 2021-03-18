import os
import unittest
from unittest import mock

from . import consent


class TestHumbugConsent(unittest.TestCase):
    def setUp(self):
        os.environ["HUMBUG_TEST_OPT_IN_AFFIRMATIVE"] = "1"
        os.environ["HUMBUG_TEST_OPT_OUT_AFFIRMATIVE"] = "1"
        os.environ["HUMBUG_TEST_OPT_IN_NEGATIVE"] = "0"
        os.environ["HUMBUG_TEST_OPT_OUT_NEGATIVE"] = "0"
        self.ev_in_not_set = os.environ.get("HUMBUG_TEST_OPT_IN_NOT_SET")
        if self.ev_in_not_set is not None:
            del os.environ["HUMBUG_TEST_OPT_IN_NOT_SET"]
        self.ev_out_not_set = os.environ.get("HUMBUG_TEST_OPT_OUT_NOT_SET")
        if self.ev_out_not_set is not None:
            del os.environ["HUMBUG_TEST_OPT_OUT_NOT_SET"]

    def tearDown(self) -> None:
        del os.environ["HUMBUG_TEST_OPT_IN_AFFIRMATIVE"]
        del os.environ["HUMBUG_TEST_OPT_OUT_AFFIRMATIVE"]
        del os.environ["HUMBUG_TEST_OPT_IN_NEGATIVE"]
        del os.environ["HUMBUG_TEST_OPT_OUT_NEGATIVE"]
        if self.ev_in_not_set is not None:
            os.environ["HUMBUG_TEST_OPT_IN_NOT_SET"] = self.ev_in_not_set
        if self.ev_out_not_set is not None:
            os.environ["HUMBUG_TEST_OPT_OUT_NOT_SET"] = self.ev_out_not_set

    def test_base_consent_affirmative(self):
        consent_state = consent.HumbugConsent(True)
        self.assertTrue(consent_state.check())

    def test_base_consent_negative(self):
        consent_state = consent.HumbugConsent(False)
        self.assertFalse(consent_state.check())

    def test_dynamic_consent_envvar_opt_in_affirmative(self):
        consent_state = consent.HumbugConsent(
            True,
            consent.environment_variable_opt_in(
                "HUMBUG_TEST_OPT_IN_AFFIRMATIVE", ["true", "1"]
            ),
        )
        self.assertTrue(consent_state.check())

    def test_dynamic_consent_envvar_opt_in_negative(self):
        consent_state = consent.HumbugConsent(
            True,
            consent.environment_variable_opt_in(
                "HUMBUG_TEST_OPT_IN_NEGATIVE", ["true", "1"]
            ),
        )
        self.assertFalse(consent_state.check())

    def test_dynamic_consent_envvar_opt_in_not_set(self):
        consent_state = consent.HumbugConsent(
            True,
            consent.environment_variable_opt_in(
                "HUMBUG_TEST_OPT_IN_NOT_SET", ["true", "1"]
            ),
        )
        self.assertFalse(consent_state.check())

    def test_dynamic_consent_envvar_opt_out_affirmative(self):
        consent_state = consent.HumbugConsent(
            True,
            consent.environment_variable_opt_out(
                "HUMBUG_TEST_OPT_OUT_AFFIRMATIVE", ["true", "1"]
            ),
        )
        self.assertFalse(consent_state.check())

    def test_dynamic_consent_envvar_opt_out_negative(self):
        consent_state = consent.HumbugConsent(
            True,
            consent.environment_variable_opt_out(
                "HUMBUG_TEST_OPT_OUT_NEGATIVE", ["true", "1"]
            ),
        )
        self.assertTrue(consent_state.check())

    def test_dynamic_consent_envvar_opt_out_not_set(self):
        consent_state = consent.HumbugConsent(
            True,
            consent.environment_variable_opt_out(
                "HUMBUG_TEST_OPT_OUT_NOT_SET", ["true", "1"]
            ),
        )
        self.assertTrue(consent_state.check())

    def test_dynamic_consent_all_allow(self):
        consent_state = consent.HumbugConsent(
            True,
            consent.environment_variable_opt_in(
                "HUMBUG_TEST_OPT_IN_AFFIRMATIVE", ["1"]
            ),
            consent.environment_variable_opt_out("HUMBUG_TEST_OPT_OUT_NEGATIVE", ["1"]),
        )
        self.assertTrue(consent_state.check())

    def test_dynamic_consent_middle_reject_opt_in_var(self):
        consent_state = consent.HumbugConsent(
            True,
            consent.environment_variable_opt_in("HUMBUG_TEST_OPT_IN_NEGATIVE", ["1"]),
            consent.environment_variable_opt_out("HUMBUG_TEST_OPT_OUT_NEGATIVE", ["1"]),
        )
        self.assertFalse(consent_state.check())

    def test_dynamic_consent_middle_reject_opt_out_var(self):
        consent_state = consent.HumbugConsent(
            True,
            consent.environment_variable_opt_in(
                "HUMBUG_TEST_OPT_IN_AFFIRMATIVE", ["1"]
            ),
            consent.environment_variable_opt_out(
                "HUMBUG_TEST_OPT_OUT_AFFIRMATIVE", ["1"]
            ),
        )
        self.assertFalse(consent_state.check())

    @mock.patch.dict(os.environ, {consent.HumbugConsent.BUGGER_OFF: "true"})
    def test_bugger_off(self):
        consent_state = consent.HumbugConsent(True)
        self.assertFalse(consent_state.check())

    @mock.patch.dict(os.environ, {consent.HumbugConsent.BUGGER_OFF: "false"})
    def test_bugger_on(self):
        consent_state = consent.HumbugConsent(True)
        self.assertTrue(consent_state.check())

    # Testing input in this way was inspired by: https://stackoverflow.com/a/6272100/13659585
    @mock.patch.object(consent, "input")
    def test_prompt_user_accept(self, user_input):
        consent_checker = consent.HumbugConsent(
            consent.prompt_user("Accept? (yes/no)", ["yes"], ["no"])
        )
        user_input.return_value = "yes"
        self.assertTrue(consent_checker.check())
        self.assertEqual(user_input.call_count, 1)

    @mock.patch.object(consent, "input")
    def test_prompt_user_reject(self, user_input):
        consent_checker = consent.HumbugConsent(
            consent.prompt_user("Accept? (yes/no)", ["yes"], ["no"])
        )
        user_input.return_value = "no"
        self.assertFalse(consent_checker.check())
        self.assertEqual(user_input.call_count, 1)

    @mock.patch.object(consent, "print")
    @mock.patch.object(consent, "input")
    def test_prompt_user_invalid_responses(self, user_input, consent_print):
        retries = 2
        consent_checker = consent.HumbugConsent(
            consent.prompt_user("Accept? (yes/no)", ["yes"], ["no"], retries=retries)
        )
        user_input.return_value = "lol"
        self.assertFalse(consent_checker.check())
        self.assertEqual(user_input.call_count, retries + 1)
        self.assertEqual(consent_print.call_count, 3 * retries)


if __name__ == "__main__":
    unittest.main()
