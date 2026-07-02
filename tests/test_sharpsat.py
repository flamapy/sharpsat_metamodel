"""Tests for the sharpsat metamodel: approximate counting and almost-uniform sampling."""
import os
import tempfile

import pytest

from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.fm_metamodel.models import FeatureModel
from flamapy.metamodels.sharpsat_metamodel.transformations import FmToSharpSAT
from flamapy.metamodels.sharpsat_metamodel.operations import (
    SharpSATConfigurationsNumber,
    SharpSATSampling,
)

# Exact oracle and validity oracle via SAT (a declared dependency, unlike BDD).
from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat
from flamapy.metamodels.pysat_metamodel.operations.pysat_configurations_number import (
    PySATConfigurationsNumber,
)
from flamapy.metamodels.pysat_metamodel.operations.pysat_satisfiable_configuration import (
    PySATSatisfiableConfiguration,
)
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration


_UVL = """features
    Root {abstract}
        optional
            A
            B
            C
            D
constraints
    (A | B) => (C <=> D)
    A => !B
"""


def _fm() -> FeatureModel:
    handle, path = tempfile.mkstemp(suffix='.uvl')
    try:
        with os.fdopen(handle, 'w') as file:
            file.write(_UVL)
        return UVLReader(path).transform()
    finally:
        os.remove(path)


def _all_feature_names(fm: FeatureModel) -> list[str]:
    return [feature.name for feature in fm.get_features()]


def _is_valid(fm: FeatureModel, selected: set) -> bool:
    sat_model = FmToPysat(fm).transform()
    elements = {name: (name in selected) for name in _all_feature_names(fm)}
    configuration = Configuration(elements)
    configuration.set_full(True)
    op = PySATSatisfiableConfiguration()
    op.set_configuration(configuration)
    return op.execute(sat_model).get_result()


def test_approximate_count_matches_exact_on_small_model():
    fm = _fm()
    exact = PySATConfigurationsNumber().execute(FmToPysat(fm).transform()).get_result()
    approx = SharpSATConfigurationsNumber().execute(FmToSharpSAT(fm).transform()).get_result()
    # ApproxMC's default (epsilon, delta) is exact on a model this small.
    assert approx == exact


def test_sampling_returns_valid_configurations():
    fm = _fm()
    model = FmToSharpSAT(fm).transform()
    op = SharpSATSampling()
    op.set_sample_size(6)
    op.set_with_replacement(True)
    sample = op.execute(model).get_sample()
    assert len(sample) == 6
    for configuration in sample:
        selected = {name for name, value in configuration.elements.items() if value}
        assert _is_valid(fm, selected), f"invalid configuration sampled: {selected}"


def test_sampling_respects_partial_configuration():
    fm = _fm()
    model = FmToSharpSAT(fm).transform()
    op = SharpSATSampling()
    op.set_sample_size(5)
    op.set_with_replacement(True)
    op.set_partial_configuration(Configuration({'A': True}))
    for configuration in op.execute(model).get_sample():
        selected = {name for name, value in configuration.elements.items() if value}
        assert 'A' in selected           # the fixed feature is always present
        assert 'B' not in selected       # A => !B forces B out


def test_without_replacement_deduplicates():
    fm = _fm()
    model = FmToSharpSAT(fm).transform()
    op = SharpSATSampling()
    op.set_sample_size(20)
    op.set_with_replacement(False)
    sample = op.execute(model).get_sample()
    keys = [frozenset(n for n, v in c.elements.items() if v) for c in sample]
    assert len(keys) == len(set(keys))   # no duplicates
