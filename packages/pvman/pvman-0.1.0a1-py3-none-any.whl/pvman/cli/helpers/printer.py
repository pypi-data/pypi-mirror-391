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


"""Helper functions designed to print unconventional types in Rich consoles."""

from rich.pretty import pprint

from dynaconf.utils.boxing import DynaBox
from dynaconf.vendor.box.box_list import BoxList


def pretty_print_setting(manager, key, config_type):
    """Print a Orbittings setting as a literal value on a Rich console.

    Parameters
    ----------
    manager : Nucleus
        A Orbittings manager instance.
    key : str, None
        The key to retrieve from `config_type`.
    config_type : str
        The OrbitalSystem object to inspect for `key`.
    """
    if key is None:
        _print_entire_config(manager, config_type)
    else:
        _print_specific_setting(manager, key, config_type)


def _print_entire_config(manager, config_type):
    """Print the entire Orbittings configuration as a dictionary on a Rich console."""
    config_dict = manager[config_type].to_dict()

    pprint(config_dict)


def _print_specific_setting(manager, key, config_type):
    """Print a Orbittings setting with their adequate type on a Rich console."""
    value = manager[config_type, key]
    formatted_value = _format_value_for_printing(value)

    pprint(formatted_value)


def _format_value_for_printing(value):
    """Format box and list Dynaconf objects to their respective literals."""
    if isinstance(value, DynaBox):
        return value.to_dict()

    if isinstance(value, BoxList):
        return value.to_list()

    return value
