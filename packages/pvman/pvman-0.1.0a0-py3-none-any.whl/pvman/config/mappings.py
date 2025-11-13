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


"""Mapping objects for the pvman configuration manager."""

from enum import Enum


class EnvvarPrefix(Enum):
    """Environment variable prefixes for pvman configuration."""

    SETTINGS = "PVMAN"
    SECRETS = "PVMAN_SECRET"


class ConfigurationDomain(Enum):
    """Configuration domain identifiers."""

    SETTINGS = "settings"
    SECRETS = "secrets"

    @classmethod
    def from_flag(cls, *, is_secret: bool) -> "ConfigurationDomain":
        """Return the appropriate domain based on the secret flag.

        Parameters
        ----------
        is_secret : bool
            Whether the configuration is secret/sensitive.

        Returns
        -------
        ConfigurationDomain
            The corresponding configuration domain.
        """
        return cls.SECRETS if is_secret else cls.SETTINGS
