"""
This module implements all Humbug methods related to generating reports and publishing them to
Bugout knowledge bases.
"""
import atexit
import concurrent.futures
from dataclasses import dataclass, field
from enum import Enum
import os
import pkg_resources
import textwrap
import time
import traceback
from typing import List, Optional
import uuid

from bugout.app import Bugout

from .consent import HumbugConsent
from .system_information import (
    SystemInformation,
    generate as generate_system_information,
)


@dataclass
class Report:
    title: str
    content: str
    tags: List[str] = field(default_factory=list)


class Modes(Enum):
    DEFAULT = 0
    SYNCHRONOUS = 1


class Reporter:
    def __init__(
        self,
        name: str,
        consent: HumbugConsent,
        client_id: Optional[str] = None,
        session_id: Optional[str] = None,
        system_information: Optional[SystemInformation] = None,
        bugout_token: Optional[str] = None,
        bugout_journal_id: Optional[str] = None,
        timeout_seconds: int = 10,
        mode: Modes = Modes.DEFAULT,
    ):
        self.name = name
        self.consent = consent
        self.client_id = client_id
        if session_id is not None:
            self.session_id = session_id
        else:
            self.session_id = str(uuid.uuid4())
        if system_information is None:
            system_information = generate_system_information()
        self.system_information = system_information
        self.bugout = Bugout()
        self.bugout_token = bugout_token
        self.bugout_journal_id = bugout_journal_id
        self.timeout_seconds = timeout_seconds

        self.report_futures: List[concurrent.futures.Future] = []
        atexit.register(self.wait)

        self.executor: Optional[concurrent.futures.Executor] = None
        if mode == Modes.DEFAULT:
            self.executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=1, thread_name_prefix="humbug_reporter"
            )

    def wait(self) -> None:
        concurrent.futures.wait(
            self.report_futures, timeout=float(self.timeout_seconds)
        )
        if self.executor is not None:
            self.executor.shutdown()

    def system_tags(self) -> List[str]:
        tags = [
            "humbug",
            "source:{}".format(self.name),
            "os:{}".format(self.system_information.os),
            "arch:{}".format(self.system_information.machine),
            "python:{}".format(self.system_information.python_version_major),
            "python:{}.{}".format(
                self.system_information.python_version_major,
                self.system_information.python_version_minor,
            ),
            "python:{}".format(self.system_information.python_version),
            "session:{}".format(self.session_id),
        ]
        if self.client_id is not None:
            tags.append("client:{}".format(self.client_id))

        return tags

    def publish(self, report: Report, wait: bool = False) -> None:
        if not self.consent.check():
            return
        if self.bugout_token is None or self.bugout_journal_id is None:
            return

        try:
            report.tags = list(set(report.tags))
            if wait or self.executor is None:
                self.bugout.create_entry(
                    token=self.bugout_token,
                    journal_id=self.bugout_journal_id,
                    title=report.title,
                    content=report.content,
                    tags=report.tags,
                    timeout=self.timeout_seconds,
                )
            else:
                report_future = self.executor.submit(
                    self.bugout.create_entry,
                    token=self.bugout_token,
                    journal_id=self.bugout_journal_id,
                    title=report.title,
                    content=report.content,
                    tags=report.tags,
                    timeout=self.timeout_seconds,
                )
                self.report_futures.append(report_future)
        except:
            pass

    def custom_report(
        self,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        publish: bool = True,
        wait: bool = False,
    ) -> Report:
        """
        Generates (and optionally publishes) a custom report in which the title, tags, and content
        are defined by the caller of this method.
        """
        if tags is None:
            tags = []
        report = Report(title=title, content=content, tags=tags)
        if publish:
            self.publish(report, wait=wait)
        return report

    def system_report(
        self, tags: Optional[List[str]] = None, publish: bool = True, wait: bool = False
    ) -> Report:
        title = "{}: System information".format(self.name)
        content = textwrap.dedent(
            """
            ### User timestamp
            ```
            {user_time}
            ```

            ### OS
            ```
            {os}
            ```

            Release: `{os_release}`

            ### Processor
            ```
            {machine}
            ```

            ### Python
            ```
            {python_version}
            ```
        """.format(
                user_time=int(time.time()),
                os=self.system_information.os,
                os_release=self.system_information.os_release,
                machine=self.system_information.machine,
                python_version=self.system_information.python_version,
            )
        )
        report = Report(title=title, content=content, tags=self.system_tags())
        if tags is not None:
            report.tags.extend(tags)

        if publish:
            self.publish(report, wait=wait)

        return report

    def error_report(
        self,
        error: Exception,
        tags: Optional[List[str]] = None,
        publish: bool = True,
        wait: bool = False,
    ) -> Report:
        title = "{} - {}".format(self.name, type(error).__name__)
        error_content = textwrap.dedent(
            """
            ### User timestamp
            ```
            {user_time}
            ```

            ### Exception summary
            ```
            {error_summary}
            ```

            ### Traceback
            ```
            {error_traceback}
            ```
        """.format(
                user_time=int(time.time()),
                error_summary=repr(error),
                error_traceback="".join(
                    traceback.format_exception(
                        etype=type(error),
                        value=error,
                        tb=error.__traceback__,
                    )
                ),
            )
        )
        if tags is None:
            tags = []
        tags.extend(self.system_tags())

        report = Report(title=title, content=error_content, tags=tags)

        if publish:
            self.publish(report, wait=wait)

        return report

    def env_report(
        self,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        publish: bool = True,
        wait: bool = False,
    ) -> Report:
        """
        Creates and optionally publishes a report containing the environment variables defined in
        the current process.
        """
        if title is None:
            title = "Environment variables"
        if tags is None:
            tags = []

        env_vars = ["{}={}".format(key, value) for key, value in os.environ.items()]
        content = "```\n{}\n```".format("\n".join(env_vars))

        report = Report(title=title, content=content, tags=tags)
        if publish:
            self.publish(report, wait=wait)
        return report

    def packages_report(
        self,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        publish: bool = True,
        wait: bool = False,
    ) -> Report:
        """
        Creates and optionally publishes a report containing the packages (and versions of those
        packages) available in the current Python process.
        """
        if title is None:
            title = "Available packages"
        if tags is None:
            tags = []

        available_packages = [
            str(package_info) for package_info in pkg_resources.working_set
        ]
        content = "```\n{}\n```".format("\n".join(available_packages))
        report = Report(title, content, tags)
        if publish:
            self.publish(report, wait=wait)
        return report

    def compound_report(
        self,
        reports: List[Report],
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        publish: bool = True,
        wait: bool = False,
    ) -> Report:
        if tags is None:
            tags = []
        for component in reports:
            tags.extend(component.tags)

        if title is None:
            title = "Composite report"

        content = "\n\n- - -\n\n".join(component.content for component in reports)

        report = Report(title=title, content=content, tags=tags)
        if publish:
            self.publish(report, wait=wait)
        return report
