# pvman
# Copyright (C) 2025 The Nummertopia Delegation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


"""Custom logger formatting utilities for pvman."""

from pvman.logging.text_tools import LoggerFormatter

LOGGER_FORMATTER = LoggerFormatter()

_FILE_BASE_TEMPLATE = (
    "{time:%Y-%m-%d %H:%M:%S}.{time:SSS} | "
    "{elapsed} | "
    "{level:<8} | "  # Based on the default levels in Loguru (max. 8 in "CRITICAL")
    "{location_string} | "
    "{message:<60} ¶"
)

FILE_FORMATTER_WITH_EXTRA = _FILE_BASE_TEMPLATE + " {extra}\n{exception}"
FILE_FORMATTER_WITHOUT_EXTRA = _FILE_BASE_TEMPLATE + "\n{exception}"


def _format_location_string(record: dict) -> str:
    """Extract and format location information as `file:line`."""
    file_name = record["file"].name
    line_number = record["line"]
    padding = LOGGER_FORMATTER.get_location_padding()

    return f"{file_name}:{line_number}".ljust(padding)


def file_formatter(record: dict) -> str:
    """Define the default formatting for Loguru calls to be stored in the log files.

    Parameters
    ----------
    record : dict
        The Loguru record dictionary with the information about the logging context.

    Returns
    -------
    str
        A formatted string with standardised padding for the individual parts of the log
        entry.
    """
    record.update({"location_string": _format_location_string(record)})

    if record["extra"]:
        return FILE_FORMATTER_WITH_EXTRA

    return FILE_FORMATTER_WITHOUT_EXTRA
