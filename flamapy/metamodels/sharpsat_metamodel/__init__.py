from flamapy.core.manifest import OperationCapability, PluginManifest
from flamapy.core.models.language_level import LanguageLevel, MajorLevel, MinorLevel

# Approximate counting (ApproxMC) and almost-uniform sampling (UniGen): never chosen by the
# planner unless the caller allows approximate results. Since 2.9 both operations pre-check
# satisfiability (pyunigen segfaults on UNSAT input) and short-circuit void models.
# Costs are estimated milliseconds from the 2026-11-06 calibration (betty synthetic models at
# 1% and 30% constraint density plus JHipster and busybox; worst case, never decreasing):
# counting takes 0.1 s at 100 features and 1.6 s at 200; from 500 features on it depends on the
# model (1.5-8 s on the dense 1,000/2,000-feature models, but the sparse 500-feature one and
# busybox did not finish within 3 minutes), so the curve carries the cap and the ceiling is the
# largest size measured.
MANIFEST = PluginManifest(
    name='sharpsat',
    calibration='2026-11-06',
    extension='sharpsat',
    supported_level=LanguageLevel(MajorLevel.BOOLEAN, {MinorLevel.GROUP_CARDINALITY}),
    max_features=2000,
    transformation_cost_curve=((200, 1), (500, 2), (1000, 4), (2000, 10)),
    operations={
        'configurations_number': OperationCapability(
            exact=False, cost_curve=((50, 30), (100, 100), (200, 1600), (500, 180000))),
        'sampling': OperationCapability(
            exact=False, cost_curve=((50, 100), (100, 420), (200, 3500), (500, 70000))),
    },
)
