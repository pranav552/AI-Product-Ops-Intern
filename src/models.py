from enum import Enum


class Buildability(str, Enum):
    BUILDABLE = "BUILDABLE"
    BUILDABLE_WITH_FRICTION = "BUILDABLE_WITH_FRICTION"
    OUTREACH_REQUIRED = "OUTREACH_REQUIRED"
    NOT_CURRENTLY_BUILDABLE = "NOT_CURRENTLY_BUILDABLE"
    NEEDS_RESEARCH = "NEEDS_RESEARCH"


def determine_buildability(
    api_exists: bool | None,
    credentials_available: bool | None,
    access_model: str,
    api_usable: bool | None,
):
    """
    Deterministic buildability classification.

    Unknown information must remain unknown.
    We do not infer missing facts.
    """

    if (
        api_exists is None
        or credentials_available is None
        or api_usable is None
    ):
        return Buildability.NEEDS_RESEARCH

    if not api_exists:
        return Buildability.NOT_CURRENTLY_BUILDABLE

    if not credentials_available:
        if access_model in {
            "PARTNER_GATED",
            "CONTACT_SALES"
        }:
            return Buildability.OUTREACH_REQUIRED

        return Buildability.NOT_CURRENTLY_BUILDABLE

    if not api_usable:
        return Buildability.NOT_CURRENTLY_BUILDABLE

    if access_model in {
        "SELF_SERVE_PAID",
        "ADMIN_APPROVAL"
    }:
        return Buildability.BUILDABLE_WITH_FRICTION

    return Buildability.BUILDABLE