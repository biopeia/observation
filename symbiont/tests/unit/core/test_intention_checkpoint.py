from __future__ import annotations

import pytest

from symbiont.core.domains.intention import IntentionDomain


def test_intention_domain_rejects_schema_one_checkpoint() -> None:
    checkpoint = IntentionDomain(organism_id="organism.intention").checkpoint()
    checkpoint["schema_version"] = 1

    with pytest.raises(ValueError, match="unsupported executive intention checkpoint"):
        IntentionDomain.restore(checkpoint, organism_id="organism.intention")
