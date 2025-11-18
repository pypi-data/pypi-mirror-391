#
# Copyright 2025 Tabs Data Inc.
#

from __future__ import annotations

import json
import os
import time

import requests
import rich_click as click

from tabsdata._cli.config_utils import Action
from tabsdata._utils.constants import TABSDATA_MODULE_NAME
from tabsdata.api.apiserver import DEFAULT_TABSDATA_DIRECTORY


class LatestVersionVerificationAction(Action):
    """
    Action that verifies if the current version is the latest one.
    """

    LATEST_VERSION_VERIFICATION_FILE = os.path.join(
        DEFAULT_TABSDATA_DIRECTORY, "version-check.json"
    )

    @property
    def timeout_in_seconds(self) -> int:
        return self.definition.get("timeout_in_seconds", 604800)  # Default to 7 days

    def execute(self, **kwargs):
        try:
            if os.path.exists(self.LATEST_VERSION_VERIFICATION_FILE):
                with open(self.LATEST_VERSION_VERIFICATION_FILE, "r") as f:
                    data = json.load(f)
                last_verification = LastVerificationContent(data)
                if (
                    time.time() - last_verification.last_checked
                    >= self.timeout_in_seconds
                ):
                    self.check(last_verification)
            else:
                last_verification = LastVerificationContent({})
                self.check(last_verification)
            if last_verification.must_print:
                last_verification.must_print = False
                click.echo(
                    "A new version of Tabsdata is available in PyPI: "
                    f"{last_verification.version}. We recommend updating to the "
                    "latest version."
                )
            last_verification.store(self.LATEST_VERSION_VERIFICATION_FILE)
        except Exception:
            pass  # Silently ignore all errors, as this is a non-critical action

    @staticmethod
    def get_latest_pypi_version(package_name: str) -> str | None:
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        versions = []
        for version_str, version_data in data["releases"].items():
            versions.append(
                PyPIPackageVersion(
                    package_name, version_str, version_data[0] if version_data else {}
                )
            )

        versions.sort(reverse=True)
        for version in versions:
            if not version.yanked:
                return version.version
        return None

    @staticmethod
    def check(verification_content: LastVerificationContent):
        import tabsdata

        last_version = LatestVersionVerificationAction.get_latest_pypi_version(
            TABSDATA_MODULE_NAME
        )
        verification_content.version = last_version
        current_version = tabsdata.__version__

        from packaging import version

        if last_version is not None and version.parse(last_version) > version.parse(
            current_version
        ):
            verification_content.must_print = True
        else:
            verification_content.must_print = False
        verification_content.last_checked = int(time.time())


class PyPIPackageVersion:
    def __init__(self, package_name: str, version: str, data: dict):
        self.package_name = package_name
        self.version = version
        self.data = data

    @property
    def yanked(self) -> bool:
        return self.data.get("yanked", False)

    def __lt__(self, other):
        from packaging import version

        return version.parse(self.version) < version.parse(other.version)

    def __eq__(self, other):
        from packaging import version

        return version.parse(self.version) == version.parse(other.version)

    def __repr__(self):
        return f"{self.package_name}=={self.version} (yanked={self.yanked})"


class LastVerificationContent:

    def __init__(self, data: dict):
        self.data = data

    @property
    def version(self) -> str:
        return self.data.get("version", "")

    @version.setter
    def version(self, value: str):
        self.data["version"] = value

    @property
    def last_checked(self) -> int:
        return self.data.get("last_checked", 0)

    @last_checked.setter
    def last_checked(self, value: int):
        self.data["last_checked"] = value

    @property
    def must_print(self) -> bool:
        return self.data.get("must_print", False)

    @must_print.setter
    def must_print(self, value: bool):
        self.data["must_print"] = value

    def store(self, file_path: str):
        with open(file_path, "w") as f:
            json.dump(self.data, f)


ACTION_CLASSES = {
    "verify_latest_version": LatestVersionVerificationAction,
    # Add other actions here
}
