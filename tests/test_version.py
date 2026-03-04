# SPDX-FileCopyrightText: 2026-present Benjamin Kusen <benjamin.kusen@gmail.com>
#
# SPDX-License-Identifier: MIT
import pytest
from taler_python.version import parse_version, check_version, LibtoolVersion


class TestParseVersion:
    """Tests for parse_version()."""

    def test_full_version_string(self):
        """Three-part version string is parsed correctly."""
        result = parse_version("27:0:5")
        assert result == LibtoolVersion(current=27, revision=0, age=5)

    def test_two_parts_age_defaults_to_zero(self):
        """When age is omitted, it defaults to 0."""
        result = parse_version("10:3")
        assert result == LibtoolVersion(current=10, revision=3, age=0)

    def test_one_part_revision_and_age_default_to_zero(self):
        """When only current is given, revision and age default to 0."""
        result = parse_version("5")
        assert result == LibtoolVersion(current=5, revision=0, age=0)

    def test_empty_string_raises(self):
        """Empty string should raise ValueError."""
        with pytest.raises(ValueError, match="must not be empty"):
            parse_version("")

    def test_too_many_parts_raises(self):
        """More than 3 colon-separated parts should raise ValueError."""
        with pytest.raises(ValueError, match="at most 3 parts"):
            parse_version("1:2:3:4")

    def test_non_numeric_raises(self):
        """Non-numeric components should raise ValueError."""
        with pytest.raises(ValueError, match="Non-numeric"):
            parse_version("abc:0:1")

    def test_zero_values(self):
        """Zero is a valid version component."""
        result = parse_version("0:0:0")
        assert result == LibtoolVersion(current=0, revision=0, age=0)


class TestCheckVersion:
    """Tests for check_version().

    The server advertises "current:revision:age" and supports client
    versions in the range [current - age, current] (inclusive).
    """

    def test_client_in_range(self):
        """Client version inside the supported range is compatible."""
        # Server: current=27, age=5 → supports [22, 27]
        assert check_version("27:0:5", 25) is True

    def test_client_at_lower_bound(self):
        """Client version exactly at (current - age) is compatible."""
        assert check_version("27:0:5", 22) is True

    def test_client_at_upper_bound(self):
        """Client version exactly at current is compatible."""
        assert check_version("27:0:5", 27) is True

    def test_client_below_range(self):
        """Client version below the supported range is incompatible."""
        assert check_version("27:0:5", 21) is False

    def test_client_above_range(self):
        """Client version above current is incompatible."""
        assert check_version("27:0:5", 28) is False

    def test_zero_age_only_exact_match(self):
        """With age=0, only the exact current version is compatible."""
        assert check_version("10:0:0", 10) is True
        assert check_version("10:0:0", 9) is False
        assert check_version("10:0:0", 11) is False
