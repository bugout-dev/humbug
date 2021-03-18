"""
This module implements Humbug's user consent mechanisms.
"""
import os
from typing import Callable, cast, Iterable, Optional, Sequence, Union

ConsentMechanism = Callable[[], bool]


class HumbugConsent:
    """
    HumbugConsent stores the client's consent settings.
    """

    BUGGER_OFF = "BUGGER_OFF"

    def __init__(self, *mechanisms: Union[bool, ConsentMechanism]) -> None:
        if not mechanisms:
            mechanisms = (False,)
        self._mechanisms = mechanisms
        self._bugger_off_mechanism = environment_variable_opt_out(self.BUGGER_OFF, yes)

    def check(self) -> bool:
        """
        Checks if all consent mechanisms signal the user's consent. If any of them signal False, returns
        False. Otherwise, returns True.
        """
        for mechanism in self._mechanisms:
            if mechanism is True:
                continue
            if mechanism is False:
                return False
            elif not cast(ConsentMechanism, mechanism)():
                return False
        # If the user has set BUGGER_OFF=yes then do not assume consent. Otherwise, at this point,
        # we can assume consent.
        return self._bugger_off_mechanism()


def environment_variable_opt_in(
    varname: str, opt_in_values: Sequence[str]
) -> ConsentMechanism:
    def mechanism() -> bool:
        if os.environ.get(varname) in opt_in_values:
            return True
        return False

    return mechanism


def environment_variable_opt_out(
    varname: str, opt_out_values: Sequence[str]
) -> ConsentMechanism:
    def mechanism() -> bool:
        if os.environ.get(varname) in opt_out_values:
            return False
        return True

    return mechanism


# yes and no are lists of values commonly used by environment variables to signify "yes" or "no"
yes = ["1", "t", "y", "T", "Y", "true", "yes", "True", "Yes", "TRUE", "YES"]
no = ["0", "f", "n", "F", "N", "false", "no", "False", "No", "FALSE", "NO"]


def prompt_user(
    prompt: str,
    accept_values: Iterable[str],
    reject_values: Iterable[str],
    retries: int = 0,
) -> ConsentMechanism:
    if accept_values is None:
        accept_values = yes
    if reject_values is None:
        reject_values = no

    def mechanism() -> bool:
        result: Optional[bool] = None
        attempts = 0
        while result is None:
            user_response = input(prompt)
            if user_response in accept_values:
                result = True
            elif user_response in reject_values:
                result = False
            else:
                if attempts >= retries:
                    result = False
                else:
                    attempts += 1
                    print("Invalid input: {}".format(user_response))
                    print(
                        "To accept, enter one of: {}".format(", ".join(accept_values))
                    )
                    print(
                        "To reject, enter one of: {}".format(", ".join(reject_values))
                    )

        return cast(bool, result)

    return mechanism
