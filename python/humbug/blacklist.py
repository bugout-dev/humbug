"""
Various implementations of the blacklist functionality.
"""
from typing import Any, Dict, List, Optional


def filter_parameters_by_key(
    blacklist_keys: List[str],
    parameters: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Applies blacklist filter to provided parameters and to 2nd layer of
    inner dictionary parameter if exists.
    """
    whitelisted_parameters: Dict[str, Any] = {}

    for key in parameters.keys():
        if key.lower() in blacklist_keys:
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
                    if inner_key.lower() in blacklist_keys:
                        continue
                    inner_dict[inner_key] = str(key_as_dict[inner_key])
                whitelisted_parameters[key] = inner_dict
                continue
            except Exception:
                pass

        whitelisted_parameters[key] = str(parameters[key])

    return whitelisted_parameters
