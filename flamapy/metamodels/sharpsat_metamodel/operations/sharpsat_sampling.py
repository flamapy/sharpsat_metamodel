from typing import Any, Optional, cast

import pyunigen

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Sampling
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.sharpsat_metamodel.models import SharpSATModel


class SharpSATSampling(Sampling):
    """Almost-uniform sampling of valid configurations with UniGen.

    Unlike an enumerate-first-N sampler, UniGen draws configurations almost uniformly at
    random. Sampling is projected onto the feature variables, and an optional partial
    configuration fixes features as assumptions.
    """

    def __init__(self, seed: int = 1) -> None:
        self._sample_size = 1
        self._with_replacement = False
        self._partial_configuration: Optional[Configuration] = None
        self._result: list[Configuration] = []
        self._seed = seed

    def set_sample_size(self, sample_size: int) -> None:
        self._sample_size = sample_size

    def set_with_replacement(self, with_replacement: bool) -> None:
        self._with_replacement = with_replacement

    def set_partial_configuration(self, partial_configuration: Configuration) -> None:
        self._partial_configuration = partial_configuration

    def get_sample(self) -> list[Configuration]:
        return self._result

    def get_result(self) -> list[Configuration]:
        return self._result

    def execute(self, model: VariabilityModel) -> 'SharpSATSampling':
        sharpsat_model = cast(SharpSATModel, model)
        sampler = pyunigen.Sampler(seed=self._seed)
        for clause in sharpsat_model.clauses:
            sampler.add_clause(clause)
        if self._partial_configuration is not None:
            for name, value in self._partial_configuration.elements.items():
                variable = sharpsat_model.variables.get(name)
                if variable is not None:
                    sampler.add_clause([variable if value else -variable])

        _cells, _hashes, samples = sampler.sample(
            num=self._sample_size, sampling_set=sharpsat_model.feature_variables()
        )

        configurations = [self._to_configuration(sharpsat_model, sample) for sample in samples]
        self._result = configurations if self._with_replacement else _dedupe(configurations)
        return self

    @staticmethod
    def _to_configuration(model: SharpSATModel, sample: list[int]) -> Configuration:
        elements: dict[Any, Any] = {}
        for literal in sample:
            if literal > 0:
                name = model.features.get(literal)
                if name is not None:
                    elements[name] = True
        return Configuration(elements)


def _dedupe(configurations: list[Configuration]) -> list[Configuration]:
    seen: set[frozenset[Any]] = set()
    unique: list[Configuration] = []
    for configuration in configurations:
        key = frozenset(name for name, value in configuration.elements.items() if value)
        if key not in seen:
            seen.add(key)
            unique.append(configuration)
    return unique
