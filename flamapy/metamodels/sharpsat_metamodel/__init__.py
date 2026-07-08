from flamapy.core.manifest import PluginManifest, OperationCapability
from flamapy.core.models.language_level import LanguageLevel, MajorLevel

# Approximate counting/sampling: scalable but not exact.
MANIFEST = PluginManifest(
    name='sharpsat',
    extension='sharpsat',
    supported_level=LanguageLevel(MajorLevel.BOOLEAN, set()),
    operations={
        'configurations_number': OperationCapability(exact=False, cost=50),
        'sampling': OperationCapability(exact=False, cost=50),
    },
)
