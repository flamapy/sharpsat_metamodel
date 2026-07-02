from typing import cast

import pyapproxmc

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import ConfigurationsNumber
from flamapy.metamodels.sharpsat_metamodel.models import SharpSATModel


class SharpSATConfigurationsNumber(ConfigurationsNumber):
    """Approximate the number of valid configurations with ApproxMC.

    Counting is projected onto the feature variables, so auxiliary variables (e.g. Tseytin
    gates) do not inflate the result. ApproxMC gives an (epsilon, delta) probabilistic
    approximation that scales far better than exact enumeration.
    """

    def __init__(self, seed: int = 1) -> None:
        self._result = 0
        self._seed = seed

    def get_configurations_number(self) -> int:
        return self._result

    def get_result(self) -> int:
        return self._result

    def execute(self, model: VariabilityModel) -> 'SharpSATConfigurationsNumber':
        sharpsat_model = cast(SharpSATModel, model)
        counter = pyapproxmc.Counter(seed=self._seed)
        for clause in sharpsat_model.clauses:
            counter.add_clause(clause)
        cell_count, hash_count = counter.count(sharpsat_model.feature_variables())
        self._result = cell_count * (2 ** hash_count)
        return self
