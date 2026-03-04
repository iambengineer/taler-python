# SPDX-FileCopyrightText: 2026-present Benjamin Kusen <benjamin.kusen@gmail.com>
#
# SPDX-License-Identifier: MIT
import httpx
import pytest
from taler_python.types.common import MerchantVersionResponse
from taler_python.clients.merchant import MerchantClient

DEMO_URL = "https://backend.demo.taler.net"

# ---------------------------------------------------------------------------
# Fixture: a snapshot of a real /config response.
# This lets us test model parsing without any network access.
# If you change the MerchantVersionResponse model, update this fixture
# to match — a failure here means the model no longer accepts previously
# valid server responses (i.e. a regression).
# ---------------------------------------------------------------------------
CONFIG_FIXTURE = {
    "currency": "KUDOS",
    "payment_target_types": "*",
    "default_persona": "expert",
    "have_self_provisioning": True,
    "have_donau": True,
    "currencies": {
        "KUDOS": {
            "name": "Kudos",
            "currency": "KUDOS",
            "common_amounts": ["KUDOS:5"],
            "num_fractional_input_digits": 2,
            "num_fractional_normal_digits": 2,
            "num_fractional_trailing_zero_digits": 2,
            "alt_unit_names": {"0": "ク"},
        }
    },
    "exchanges": [
        {
            "master_pub": "F80MFRG8HVH6R9CQ47KRFQSJP3T6DBJ4K1D9B703RJY3Z39TBMJ0",
            "currency": "KUDOS",
            "base_url": "https://exchange.demo.taler.net/",
        }
    ],
    "mandatory_tan_channels": ["email"],
    "implementation": "urn:net:taler:specs:taler-merchant:c-reference",
    "name": "taler-merchant",
    "version": "23:1:11",
}


def _demo_is_reachable() -> bool:
    """Return True if the demo server responds, False otherwise."""
    try:
        httpx.get(f"{DEMO_URL}/config", timeout=5)
        return True
    except (httpx.HTTPError, httpx.ConnectError):
        return False


# ---------------------------------------------------------------------------
# 1. Fixture test — no network, catches model regressions
# ---------------------------------------------------------------------------
class TestMerchantVersionResponseModel:
    """Validate MerchantVersionResponse against a hardcoded JSON fixture."""

    def test_fixture_parses_successfully(self):
        """The model should accept a known-good server response."""
        result = MerchantVersionResponse.model_validate(CONFIG_FIXTURE)

        # Spot-check a few fields to make sure values came through correctly
        assert result.name == "taler-merchant"
        assert result.currency == "KUDOS"
        assert result.version == "23:1:11"
        assert result.have_donau is True
        assert len(result.exchanges) == 1
        assert result.exchanges[0].base_url == "https://exchange.demo.taler.net/"

    def test_missing_required_field_raises(self):
        """Removing a required field should cause a validation error.

        This proves the model actually enforces its schema — if every
        field were Optional, this test would fail, alerting you to a
        weakened model.
        """
        broken = {**CONFIG_FIXTURE}
        del broken["name"]  # 'name' is Literal["taler-merchant"], required

        with pytest.raises(Exception):  # Pydantic ValidationError
            MerchantVersionResponse.model_validate(broken)

    def test_wrong_name_literal_raises(self):
        """The 'name' field is Literal["taler-merchant"]; other values
        should be rejected."""
        broken = {**CONFIG_FIXTURE, "name": "not-taler-merchant"}

        with pytest.raises(Exception):
            MerchantVersionResponse.model_validate(broken)


# ---------------------------------------------------------------------------
# 2. Integration test — hits the live demo, catches spec drift
# ---------------------------------------------------------------------------
@pytest.mark.skipif(
    not _demo_is_reachable(),
    reason="Demo server not reachable — skipping integration test",
)
class TestMerchantIntegration:
    """Integration tests that talk to the live demo backend."""

    def test_live_config_parses(self):
        """Fetch /config from the live demo and validate against our model.

        If this fails but the fixture test passes, the upstream API has
        changed (spec drift) and our model needs updating.
        """
        response = httpx.get(f"{DEMO_URL}/config", timeout=10)
        response.raise_for_status()

        result = MerchantVersionResponse.model_validate(response.json())

        # Basic sanity — the demo should always identify as taler-merchant
        assert result.name == "taler-merchant"
        assert result.currency  # non-empty string

    def test_merchant_client_init(self):
        """MerchantClient should initialize without error against the demo."""
        with MerchantClient(DEMO_URL) as client:
            config = client.get_config()
            assert config.name == "taler-merchant"
