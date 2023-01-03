# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/95_Logger.ipynb.

# %% auto 0
__all__ = ['Logger', 'TracebackDetails']

# %% ../nbs/95_Logger.ipynb 3
import datetime as dt

from typing import Optional, List
from dataclasses import dataclass

import traceback

from fastcore.basics import patch_to


# %% ../nbs/95_Logger.ipynb 4
class Logger:
    """log class with user customizeable output method"""

    root_module: str
    app_name: str

    logs: List[dict]
    breadcrumb: Optional[list]

    # function to call with write_logs method.
    output_fn: Optional[callable] = None

    def __init__(
        self,
        app_name: str,  # name of the app for grouping logs
        root_module: Optional[str] = "<module>",  # root module for stack trace
        output_fn: Optional[
            callable
        ] = None,  # function to call with write_logs method.
    ):

        self.app_name = app_name
        self.output_fn = output_fn
        self.root_module = root_module
        self.logs = []
        self.breadcrumb = []

    def _add_crumb(self, crumb):
        if crumb not in self.breadcrumb:
            self.breadcrumb.append(crumb)

    def _remove_crumb(self, crumb):
        if crumb in self.breadcrumb:
            self.breadcrumb.remove(crumb)

# %% ../nbs/95_Logger.ipynb 6
@patch_to(Logger)
def _get_traceback(
    self,
    root_module: str = "<module>",
    num_stacks_to_drop=0,  # drop entries from the top of stack to exclude the functions that retrieve the traceback
) -> [traceback.FrameSummary]:  # returns a filtered list of FrameSummaries from traceback
    """method that retrieves traceback"""

    tb = traceback.extract_stack()

    # find the last module index
    module_index = 0
    for index, tb_line in enumerate(tb):
        function_name = tb_line[2]

        if function_name == root_module:
            module_index = index

    if num_stacks_to_drop == 0:
        return tb[module_index:]

    return tb[module_index:-num_stacks_to_drop]

# %% ../nbs/95_Logger.ipynb 8
@dataclass
class TracebackDetails:
    """result of _get_traceback_details function"""

    function_name: str
    file_name: str
    function_trail: str


@patch_to(Logger)
def _get_traceback_details(
    self,
    traceback_list: [
        traceback.FrameSummary
    ],  # clean list of frame summaries from traceback (be sure to exclude frames from functions that retrieved the traceback)
) -> TracebackDetails:  # descriptive summary from the top of the traceback
    """returns TracebackDetails, for the entry at the top of the stack"""

    function_trail = " -> ".join([line[2] for line in traceback_list])

    function_name = traceback_list[-1][2]
    file_name = traceback_list[-1][0]

    return TracebackDetails(function_name, file_name, function_trail)

# %% ../nbs/95_Logger.ipynb 14
@patch_to(Logger)
def _add_log(
    self, message: str, type_str: str, debug=False, num_stacks_to_drop=3
) -> dict:
    """internal method to append message to log"""

    traceback_list = self._get_traceback(num_stacks_to_drop=num_stacks_to_drop)

    if debug:
        print({"num_stacks_to_drop": num_stacks_to_drop})
        print([tb_line[2] for tb_line in traceback_list])

    new_row = {
        "date_time": dt.datetime.now(),
        "application": self.app_name,
        "log_type": type_str,
        "log_message": message,
        "breadcrumb": "->".join(self.breadcrumb),
    }

    traceback_details = self._get_traceback_details(traceback_list)

    new_row.update(
        {
            "function_name": traceback_details.function_name,
            "file_name": traceback_details.file_name,
            "function_trail": traceback_details.function_trail,
        }
    )

    if debug:
        print(new_row)

    self.logs.append(new_row)

    return new_row


@patch_to(Logger)
def log_info(self, message, debug=False, num_stacks_to_drop=3):
    """log an informational message"""
    return self._add_log(
        message=message,
        type_str="Info",
        num_stacks_to_drop=num_stacks_to_drop,
        debug=debug,
    )


@patch_to(Logger)
def log_error(self, message, debug=False, num_stacks_to_drop=3):
    """log an error message"""

    return self._add_log(
        message=message,
        type_str="Error",
        num_stacks_to_drop=num_stacks_to_drop,
        debug=debug,
    )


@patch_to(Logger)
def log_warning(self, message, debug=False, num_stacks_to_drop=3):
    """log a warning message"""

    return self._add_log(
        message=message,
        type_str="Warning",
        num_stacks_to_drop=num_stacks_to_drop,
        debug=debug,
    )

# %% ../nbs/95_Logger.ipynb 17
@patch_to(Logger)
def output_log(self):
    """calls the user defined output function"""
    return self.output_fn(self.logs)
