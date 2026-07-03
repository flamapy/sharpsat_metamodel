"""Tests for the sharpsat metamodel: approximate counting and almost-uniform sampling."""
import os
import tempfile
from itertools import product

import pytest

from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.fm_metamodel.models import FeatureModel, ClauseSet
from flamapy.metamodels.sharpsat_metamodel.transformations import FmToSharpSAT
from flamapy.metamodels.sharpsat_metamodel.operations import (
    SharpSATConfigurationsNumber,
    SharpSATSampling,
)
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration


# Exact oracle: enumerate the valid configurations by brute-forcing the CNF produced by
# fm_metamodel's solver-agnostic ClauseSet — no SAT backend, so the tests only depend on
# flamapy-fm (already required) and match sharpsat's own encoding path.
def _valid_configs(fm: FeatureModel) -> set:
    """Valid configurations as frozensets of selected feature names."""
    clause_set = ClauseSet.from_feature_model(fm)
    name_of = {vid: name for name, vid in clause_set.variables.items()}
    var_ids = sorted({abs(lit) for clause in clause_set.clauses for lit in clause}
                     | set(clause_set.variables.values()))
    configs = set()
    for bits in product((False, True), repeat=len(var_ids)):
        assignment = dict(zip(var_ids, bits))
        if all(any((lit > 0) == assignment[abs(lit)] for lit in clause)
               for clause in clause_set.clauses):
            configs.add(frozenset(name_of[v] for v in var_ids if assignment[v] and v in name_of))
    return configs


def _exact_count(fm: FeatureModel) -> int:
    return len(_valid_configs(fm))


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
    return frozenset(selected) in _valid_configs(fm)


_IMPLIED_VARS_UVL = """features
    Root {abstract}
        mandatory
            Base
                mandatory
                    Core
        optional
            A
            B
            C
constraints
    A => B
"""


def _fm_from(uvl):
    handle, path = tempfile.mkstemp(suffix='.uvl')
    try:
        with os.fdopen(handle, 'w') as file:
            file.write(uvl)
        return UVLReader(path).transform()
    finally:
        os.remove(path)


def test_approximate_count_matches_exact_on_small_model():
    fm = _fm()
    exact = _exact_count(fm)
    approx = SharpSATConfigurationsNumber().execute(FmToSharpSAT(fm).transform()).get_result()
    # ApproxMC's default (epsilon, delta) is exact on a model this small.
    assert approx == exact


def test_count_is_correct_with_implied_variables():
    # Regression guard: models with implied variables (mandatory chains, root unit clause)
    # must not be undercounted. The standalone pyapproxmc binding halved these; the UniGen
    # ApproxMC invocation used by the counter does not.
    fm = _fm_from(_IMPLIED_VARS_UVL)
    exact = _exact_count(fm)
    approx = SharpSATConfigurationsNumber().execute(FmToSharpSAT(fm).transform()).get_result()
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
