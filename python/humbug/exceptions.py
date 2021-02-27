"""
Humbug exceptions for inheritance by created user classes.
"""
from .report import Reporter


class ExceptionWithReporting(Exception):
    def __init__(self, bugout_reporter: Reporter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bugout_reporter.error_report(self, publish=True)


class ValueErrorWithReporting(ValueError):
    def __init__(self, bugout_reporter: Reporter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bugout_reporter.error_report(self, publish=True)
