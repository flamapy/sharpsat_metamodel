from flamapy.core.manifest import PluginManifest, OperationCapability
from flamapy.core.models.language_level import LanguageLevel, MajorLevel

# Approximate counting/sampling: scalable but not exact. 2.8 calibration only covered
# small satisfiable models (0.2ms at <=50 features): pyunigen segfaults the process on
# UNSAT formulas — a plugin bug to fix (pre-check satisfiability before invoking unigen).
MANIFEST = PluginManifest(
    name='sharpsat',
    extension='sharpsat',
    supported_level=LanguageLevel(MajorLevel.BOOLEAN, set()),
    operations={
        'configurations_number': OperationCapability(exact=False, cost=50),
        'sampling': OperationCapability(exact=False, cost=50),
    },
)
