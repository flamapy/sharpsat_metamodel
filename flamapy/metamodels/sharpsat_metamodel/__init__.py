from flamapy.core.manifest import PluginManifest, OperationCapability
from flamapy.core.models.language_level import LanguageLevel, MajorLevel

# Approximate counting/sampling: scalable but not exact. Since 2.9 both operations
# pre-check satisfiability (pyunigen segfaults on UNSAT input) and short-circuit void
# models; costs from the 2.9 calibration refresh.
MANIFEST = PluginManifest(
    name='sharpsat',
    extension='sharpsat',
    supported_level=LanguageLevel(MajorLevel.BOOLEAN, set()),
    operations={
        'configurations_number': OperationCapability(exact=False, cost=50),
        'sampling': OperationCapability(exact=False, cost=50),
    },
)
