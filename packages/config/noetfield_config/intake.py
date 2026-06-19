"""Canonical operational intake email — Google Workspace inbox (active)."""

CANONICAL_INTAKE_EMAIL = "operations@noetfield.com"

# Legacy aliases — do not use in user-facing copy; map in deliverability configs only.
LEGACY_INTAKE_ALIASES = frozenset(
    {
        "contact@noetfield.com",
        "procurement@noetfield.com",
        "sales@noetfield.com",
        "engagements@noetfield.com",
    }
)

COMPLIANCE_REMEDIATION_TIP = (
    f"Manual compliance review: contact {CANONICAL_INTAKE_EMAIL} with evaluation ID and tenant context."
)
