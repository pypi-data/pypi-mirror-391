"""Common logging utilities."""

import traceback

import orjson


def error_to_json(error: Exception, dump: bool = True) -> str | dict:
    """Get error message (with stack trace) from an exception into a single JSON-serializable string (or dict).

    This is useful for logging to a single line in the logs, which allows easy identification the associated exception,
    rather than wondering which part of the logs belong to the same exception thrown.

    Args:
        error: The exception to convert to a JSON (or dict).
        dump: If True, will return the error message as a JSON string.

    Returns:
        If `dump` is True, returns the error message (with stack trace) from the exception as a JSON string.
        Otherwise, returns the error message (with stack trace) from the exception as a dict.
    """
    error_dic = {"traceback": "".join(traceback.format_exception(type(error), error, error.__traceback__))}
    # case: httpx.HTTPStatusError (hopefully)
    if hasattr(error, "response") and hasattr(error.response, "text"):
        error_dic["response"] = error.response.text
    if dump:
        return orjson.dumps(error_dic).decode()
    return error_dic

