"""Compatibility exports for body definitions split into per-body modules.

Import morphology-specific specifications from ``crawler`` or ``asymmetric``.
"""

from embodiment.physics3d.asymmetric import ASYMMETRIC_SPEC, AsymmetricPhysics
from embodiment.physics3d.crawler import CRAWLER_SPEC, CrawlerPhysics
from embodiment.physics3d.mechanics import GROUND_MATERIAL

__all__ = [
    "ASYMMETRIC_SPEC",
    "AsymmetricPhysics",
    "CRAWLER_SPEC",
    "CrawlerPhysics",
    "GROUND_MATERIAL",
]
