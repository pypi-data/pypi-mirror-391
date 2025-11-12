from importlib.metadata import version

from termcolor import colored
from update_checker import UpdateChecker, UpdateResult


_COMMAND_NAME = "v-cr"
_PACKAGE_NAME = "v-magic-code-review"


def update_check():
    local_version = _get_local_version()
    checker = UpdateChecker()
    result: UpdateResult = checker.check(_PACKAGE_NAME, local_version)
    if result:
        message = (
            f"Warning! {_COMMAND_NAME} update available! {local_version} → {result.available_version}, "
            f"Please update with \"pipx upgrade {_COMMAND_NAME}\""
            f"\n"
        )
        print(colored(message, color='yellow', attrs=['bold']))


def print_version_text() -> None:
    local_version = _get_local_version()
    print("{} {}".format(
        colored(_COMMAND_NAME, color='green', attrs=['bold']),
        colored(local_version, color='red', attrs=['bold'])
    ))


def _get_local_version():
    return version(_PACKAGE_NAME)
