"""
Various implementations of the blacklist functionality.
"""
from typing import Any, Callable, Dict, List, Optional


def generate_filter_parameters_by_key_fn(
    blacklist_keys: List[str],
) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """
    Generates a parameter filter function which filters out the parameters whose names are in the given
    list of blacklist_keys.

    The comparison to blacklist_keys is case insensitive.
    """

    lowercase_blacklist_keys = [key.lower() for key in blacklist_keys]

    def filter_parameters_by_key(
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            k: str(v)
            for k, v in parameters.items()
            if k.lower() not in lowercase_blacklist_keys
        }

    return filter_parameters_by_key


def generate_filter_parameters_by_key_inner_fn(
    blacklist_keys: List[str],
) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """
    Generates a parameter filter function which filters out the parameters whose names are in the given
    list of blacklist_keys for 1st and 2nd layer of dictionary. Expands pydantic model to dictionary.

    The comparison to blacklist_keys is case insensitive.
    """

    lowercase_blacklist_keys = [key.lower() for key in blacklist_keys]

    def filter_parameters_by_key_inner(
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Applies blacklist filter to provided parameters and to 2nd layer of
        inner dictionary parameter if exists.
        """
        whitelisted_parameters: Dict[str, Any] = {}

        for key in parameters.keys():
            if key.lower() in lowercase_blacklist_keys:
                continue

            key_as_dict: Optional[Dict[str, Any]] = None
            for d in dir(parameters[key]):
                if d == "keys":
                    key_as_dict = parameters[key]
                    break
                elif d == "dict":  # Pydantic models support
                    key_as_dict = parameters[key].dict()
                    break

            if key_as_dict is not None:
                try:
                    inner_dict: Dict[str, str] = {}
                    for inner_key in key_as_dict.keys():
                        if inner_key.lower() in lowercase_blacklist_keys:
                            continue
                        inner_dict[inner_key] = str(key_as_dict[inner_key])
                    whitelisted_parameters[key] = inner_dict
                    continue
                except Exception:
                    pass

            whitelisted_parameters[key] = str(parameters[key])

        return whitelisted_parameters

    return filter_parameters_by_key_inner
