from src.models import (
    Buildability,
    determine_buildability,
)


def test_self_serve_public_api():
    result = determine_buildability(
        api_exists=True,
        credentials_available=True,
        access_model="SELF_SERVE_FREE",
        api_usable=True,
    )

    assert result == Buildability.BUILDABLE


def test_paid_api():
    result = determine_buildability(
        api_exists=True,
        credentials_available=True,
        access_model="SELF_SERVE_PAID",
        api_usable=True,
    )

    assert result == Buildability.BUILDABLE_WITH_FRICTION


def test_partner_gated():
    result = determine_buildability(
        api_exists=True,
        credentials_available=False,
        access_model="PARTNER_GATED",
        api_usable=True,
    )

    assert result == Buildability.OUTREACH_REQUIRED


def test_no_api():
    result = determine_buildability(
        api_exists=False,
        credentials_available=False,
        access_model="UNKNOWN",
        api_usable=False,
    )

    assert result == Buildability.NOT_CURRENTLY_BUILDABLE


def test_unknown_information():
    result = determine_buildability(
        api_exists=None,
        credentials_available=None,
        access_model="UNKNOWN",
        api_usable=None,
    )

    assert result == Buildability.NEEDS_RESEARCH