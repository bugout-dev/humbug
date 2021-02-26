"""
This module implements Humbug's user consent mechanisms.
"""
import os
from typing import Callable, cast, Sequence, Union

ConsentMechanism = Callable[[], bool]


class HumbugConsent:
    """
    HumbugConsent stores the client's consent settings.
    """

    def __init__(self, *mechanisms: Union[bool, ConsentMechanism]) -> None:
        if not mechanisms:
            mechanisms = (False,)
        self._mechanisms = mechanisms

    def check(self) -> bool:
        """
        Checks if all consent mechanisms signal the user's consent. If any of them signal False, returns
        False. Otherwise, returns True.
        """
        for mechanism in self._mechanisms:
            if mechanism is True:
                continue
            elif mechanism is False:
                return False
            elif not cast(ConsentMechanism, mechanism)():
                return False
        return True


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
